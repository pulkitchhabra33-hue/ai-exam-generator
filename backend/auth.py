from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import User

from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

router= APIRouter()

secret_key= "my_secret_key"

oauth2_scheme= OAuth2PasswordBearer(tokenUrl= "login")

algorithm= "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES= 60

pwd_context= CryptContext(schemes= ["pbkdf2_sha256"], deprecated= "auto")

class UserRequest(BaseModel):
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
def signup(user: UserRequest):
    db: Session= SessionLocal()

    existing_user= db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code= 400, detail= "Email already registered")
    
    hashed_password= get_password_hash(user.password)
    new_user= User(email= user.email, password= hashed_password,
                   plan= "FREE", credits_remaining= 2)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}

#Login
@router.post("/login")
def login(user: UserRequest):
    db: Session= SessionLocal()

    existing_user= db.query(User).filter(User.email == user.email).first()
    if not existing_user:
        raise HTTPException(status_code= 400, detail= "Invalid email or password")
    if not verify_password(user.password, existing_user.password):
        raise HTTPException(status_code= 400, detail= "Invalid email or password")
    
    access_token= create_access_token(data= {"sub": existing_user.email})
    return {"access_token": access_token, "token_type": "bearer"}