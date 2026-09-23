from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.security import OAuth2PasswordBearer

from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import User, PaperHistory, GuestSession

from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

from dotenv import load_dotenv
import os
import uuid
import hashlib
import secrets

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

@router.post("/upgrade-plan")
def upgrade_plan(data: UpgradeRequest, current_user= Depends(get_current_user)):
    db: Session= SessionLocal()
    user= db.query(User).filter(User.id == current_user.id).first()

    if data.plan == "PRO":
        user.plan= "PRO"
        user.credits_remaining= 80

        user.subscription_end= (
            datetime.utcnow() +
            timedelta(days= 30)
        )

    elif data.plan == "PREMIUM":
        user.plan= "PREMIUM"
        user.credits_remaining= 400
        user.subscription_end= (
            datetime.utcnow() +
            timedelta(days= 120)
        )

    else:
        raise HTTPException(status_code= 400, detail= "Invalid plan selected")
    
    db.commit()
    db.refresh(user)
    return {
        "message":
            f"Plan upgraded to {user.plan}",

        "credits":
            user.credits_remaining
    }
    

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