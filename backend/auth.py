from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.security import OAuth2PasswordBearer

from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import User, PaperHistory, GuestSession, Payment
from backend import plans

from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

from dotenv import load_dotenv
import os
import uuid
import hashlib
import secrets
import razorpay

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str

router= APIRouter()

load_dotenv()

secret_key= os.getenv("SECRET_KEY")

if not secret_key:
    raise RuntimeError(
        "SECRET_KEY environment variable is not configured."
    )

razorpay_key_id= os.getenv("RAZORPAY_KEY_ID")
razorpay_key_secret= os.getenv("RAZORPAY_KEY_SECRET")

if not razorpay_key_id or not razorpay_key_secret:
    raise RuntimeError(
        "Razorpay API credentials are not configured."
    )

razorpay_client= razorpay.Client(
    auth=(
        razorpay_key_id,
        razorpay_key_secret
    )
)

oauth2_scheme= OAuth2PasswordBearer(tokenUrl= "login")

algorithm= "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES= 60

pwd_context= CryptContext(schemes= ["pbkdf2_sha256"], deprecated= "auto")

class UserRequest(BaseModel):
    name: str
    email: str
    password: str

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode= data.copy()
    expire= datetime.utcnow() + timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    
    encoded_jwt= jwt.encode(to_encode, secret_key, algorithm= algorithm)

    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload= jwt.decode(token, secret_key, algorithms= [algorithm])
        email: str= payload.get("sub")

        if email is None:
            raise HTTPException(status_code= 401, detail= "AUTHENTICATION REQUIRED")
    except JWTError:
        raise HTTPException(status_code= 401, detail= "AUTHENTICATION REQUIRED")
    
    db= SessionLocal()

    try:
        user= db.query(User).filter(User.email == email).first()
    
        if user is None:
            raise HTTPException(status_code= 401, detail= "AUTHENTICATION REQUIRED")

        return user

    finally:
        db.close()


#SIGNUP
@router.post("/signup")
def signup(user: SignupRequest):
    db: Session= SessionLocal()

    try:
        existing_user= (
            db.query(User)
            .filter(User.email == user.email)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code= 400,
                detail="Email already registered"
            )

        hashed_password= get_password_hash(
            user.password
        )

        new_user= User(
            name= user.name,
            email= user.email,
            password= hashed_password,
            plan= "FREE",
            credits_remaining= 10
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        access_token= create_access_token(
            data={"sub": new_user.email}
        )

        return {
            "message": "User created successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "name": new_user.name,
                "email": new_user.email
            }
        }

    finally:
        db.close()


#Login
@router.post("/login")
def login(user: LoginRequest):
    db: Session = SessionLocal()

    try:
        existing_user= (
            db.query(User)
            .filter(User.email == user.email)
            .first()
        )

        if not existing_user:

            raise HTTPException(
                status_code=400,
                detail="Invalid email or password"
            )

        if not verify_password(
            user.password,
            existing_user.password
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid email or password"
            )

        access_token= create_access_token(
            data={
                "sub": existing_user.email
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    finally:
        db.close()


# Guest-ID
@router.post("/guest-session")
def create_guest_session(
    request: Request,
    response: Response
):
    db: Session = SessionLocal()

    try:
        identity_token = request.cookies.get("guest_identity")

        guest = None

        # 1. Recover guest using persistent identity cookie
        if identity_token:
            identity_token_hash = hashlib.sha256(
                identity_token.encode()
            ).hexdigest()

            guest = (
                db.query(GuestSession)
                .filter(
                    GuestSession.identity_token_hash == identity_token_hash
                )
                .first()
            )

        # 2. Fallback: recover using existing guest ID
        if guest is None:
            guest_id = request.headers.get("X-Guest-ID")

            if guest_id:
                guest = (
                    db.query(GuestSession)
                    .filter(
                        GuestSession.guest_id == guest_id
                    )
                    .first()
                )

        # 3. Create a guest only when no existing session can be recovered
        if guest is None:
            guest = GuestSession(
                guest_id=str(uuid.uuid4()),
                credits_remaining=10
            )

            db.add(guest)
            db.flush()

        # 4. Rotate identity cookie when missing or invalid
        if not identity_token or guest.identity_token_hash is None:
            identity_token = secrets.token_urlsafe(32)

            identity_token_hash = hashlib.sha256(
                identity_token.encode()
            ).hexdigest()

            guest.identity_token_hash = identity_token_hash

        db.commit()
        db.refresh(guest)

        # 5. Set persistent identity cookie
        response.set_cookie(
            key="guest_identity",
            value=identity_token,
            max_age=60 * 60 * 24 * 365,
            httponly=True,
            secure=True,
            samesite="none",
            path="/"
        )

        return {
            "guest_id": guest.guest_id,
            "credits_remaining": guest.credits_remaining
        }

    finally:
        db.close()

def get_guest_session(guest_id, db):
    if not guest_id:
        return None

    guest= (
        db.query(GuestSession).filter(
            GuestSession.guest_id == guest_id
        )
        .first()
    )

    return guest

class UpgradeRequest(BaseModel):
    plan: str

class CreateOrderRequest(BaseModel):
    plan:str

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@router.post("/create-order")
def create_razorpay_order(
    data: CreateOrderRequest,
    current_user= Depends(get_current_user)
):
    plan= data.plan.upper()

    if plan not in ["PRO", "PREMIUM"]:
        raise HTTPException(
            status_code= 400,
            detail= "Invalid plan selected."
        )

    plan_details= plans.PLANS.get(plan)

    if not plan_details:
        raise HTTPException(
            status_code=400,
            detail="Plan configuration not found."
        )

    amount= plan_details["price"] * 100

    try:
        order= razorpay_client.order.create(
            data={
                "amount": amount,
                "currency": "INR",
                "receipt": str(uuid.uuid4()),
                "notes": {
                    "user_id": str(current_user.id),
                    "plan": plan
                }
            }
        )

        return {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key_id": razorpay_key_id,
            "plan": plan
        }

    except Exception as e:
        print(
            f"Razorpay order creation failed: {str(e)}"
        )

        raise HTTPException(
            status_code=502,
            detail="Unable to create payment order."
        )

@router.post("/verify-payment")
def verify_payment(
    data: VerifyPaymentRequest,
    current_user=Depends(get_current_user)
):
    db: Session = SessionLocal()

    try:
        # 1. Verify Razorpay signature
        try:
            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id": data.razorpay_order_id,
                "razorpay_payment_id": data.razorpay_payment_id,
                "razorpay_signature": data.razorpay_signature
            })

        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Payment signature verification failed."
            )

        # 2. Check for duplicate payment/order
        existing_payment = db.query(Payment).filter(
            (Payment.razorpay_order_id == data.razorpay_order_id) |
            (Payment.razorpay_payment_id == data.razorpay_payment_id)
        ).first()

        if existing_payment:
            if (
                existing_payment.razorpay_order_id == data.razorpay_order_id
                and existing_payment.razorpay_payment_id == data.razorpay_payment_id
                and existing_payment.user_id == current_user.id
                and existing_payment.status == "SUCCESS"
            ):
                return {
                    "message": "Payment has already been processed.",
                    "plan": existing_payment.plan,
                    "credits": existing_payment.credits_added,
                    "already_processed": True
                }

            raise HTTPException(
                status_code=409,
                detail="Payment or order ID has already been used."
            )
        
        # 3. Fetch order and payment directly from Razorpay

        order = razorpay_client.order.fetch(
            data.razorpay_order_id
        )

        payment = razorpay_client.payment.fetch(
            data.razorpay_payment_id
        )

        # 4. Validate order ownership
        if str(order.get("notes", {}).get("user_id")) != str(current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Payment order does not belong to this user."
            )

        # 5. Validate payment-order relationship
        if payment.get("order_id") != data.razorpay_order_id:
            raise HTTPException(
                status_code=400,
                detail="Payment does not match the order."
            )

        # 6. Confirm payment was captured
        if payment.get("status") != "captured":
            raise HTTPException(
                status_code=400,
                detail="Payment has not been captured."
            )

        # 7. Validate plan and amount using backend configuration
        plan = order.get("notes", {}).get("plan")

        plan_details = plans.PLANS.get(plan)

        if not plan_details:
            raise HTTPException(
                status_code=400,
                detail="Invalid payment plan."
            )

        expected_amount = plan_details["price"] * 100

        if (
            order.get("amount") != expected_amount
            or payment.get("amount") != expected_amount
            or payment.get("currency") != "INR"
            or order.get("currency") != "INR"
        ):
            raise HTTPException(
                status_code=400,
                detail="Payment amount or currency mismatch."
            )

        if order.get("status") != "paid":
            raise HTTPException(
                status_code=400,
                detail="Order has not been paid."
            )

        # 8. Get user from database
        user = db.query(User).filter(
            User.id == current_user.id
        ).with_for_update().first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        # 9. Determine credits and subscription duration
        credits = plan_details["credits"]

        duration_days = 30 if plan == "PRO" else 120

        # 10. Save payment record
        new_payment = Payment(
            user_id=user.id,
            razorpay_order_id=data.razorpay_order_id,
            razorpay_payment_id=data.razorpay_payment_id,
            plan=plan,
            amount=expected_amount,
            credits_added=credits,
            status="SUCCESS"
        )

        db.add(new_payment)

        # 11. Allocate credits only after verification
        user.plan = plan
        user.credits_remaining = credits
        user.subscription_end = (
            datetime.utcnow() + timedelta(days=duration_days)
        )

        db.commit()

        db.refresh(user)

        return {
            "message": "Payment verified successfully.",
            "plan": user.plan,
            "credits": user.credits_remaining,
            "subscription_end": user.subscription_end
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()

        print(f"Payment verification failed: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail="Unable to verify payment."
        )

    finally:
        db.close()


@router.post("/upgrade-plan")
def upgrade_plan(
    current_user=Depends(get_current_user)
):
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use verified Razorpay payments."
    )
    

@router.get("/current-user")
def current_user_info(current_user= Depends(get_current_user)):

    return{
        "name": current_user.name,
        "email": current_user.email,
        "plan": current_user.plan,
        "credits": current_user.credits_remaining,
        "subscription_end": current_user.subscription_end,
        "status": "Active" if current_user.plan != "FREE" else "Free Plan"
    }

@router.get("/my-papers")
def get_my_papers(current_user= Depends(get_current_user)):
    db: Session= SessionLocal()
    papers= db.query(PaperHistory).filter(PaperHistory.user_id == current_user.id).all()
    return papers