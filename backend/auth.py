from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import User, PaperHistory, GuestSession

from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from dotenv import load_dotenv
import os
import uuid

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
    payload= jwt.decode(token, secret_key, algorithms= [algorithm])
    email: str= payload.get("sub")

    if email is None:
        raise HTTPException(status_code= 401, detail= "Invalid authentication credentials")
    
    db= SessionLocal()
    user= db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise HTTPException(status_code= 401, detail= "Invalid authentication credentials")

    return user


#SIGNUP
@router.post("/signup")
def signup(user: SignupRequest):
    db: Session= SessionLocal()

    try:
        existing_user= {
            db.query(User)
            .filter(User.email == user.email)
            .first()
        }

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
            credits_remaining= 2
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User created success"
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


#Guest-ID
@router.post("/guest-session")
def create_guest_session():
    db: Session= SessionLocal()
    guest_id= str(uuid.uuid4())

    guest= GuestSession(guest_id= guest_id, credits_remaining= 2)
    db.add(guest)
    db.commit()

    db.refresh(guest)
    db.close()

    return {
        "guest_id": guest_id,
        "credits_remaining": guest.credits_remaining
    }

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
        user.credits_remaining= 75

        user.subscription_end= (
            datetime.utcnow() +
            timedelta(days= 30)
        )

    elif data.plan == "PREMIUM":
        user.plan= "PREMIUM"
        user.credits_remaining= 600
        user.subscription_end= (
            datetime.utcnow() +
            timedelta(days= 365)
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