from sqlalchemy import Column, Integer, String
from sqlalchemy import DateTime
from datetime import datetime
from backend.database import Base

class User(Base):
    __tablename__= "users"

    id= Column(Integer, primary_key= True, index= True)
    email= Column(String(255), unique= True, index= True)
    password= Column(String(255))

    plan= Column(String(20), default= "FREE")
    credits_remaining= Column(Integer, default=2)
    subscription_end= Column(DateTime, nullable= True)

    created_at= Column(DateTime, default= datetime.utcnow)