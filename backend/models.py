from sqlalchemy import Column, Integer, String
from sqlalchemy import DateTime
from datetime import datetime
from backend.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__= "users"

    id= Column(Integer, primary_key= True, index= True)
    email= Column(String(255), unique= True, index= True)
    password= Column(String(255))

    plan= Column(String(20), default= "FREE")
    credits_remaining= Column(Integer, default=2)
    subscription_end= Column(DateTime, nullable= True)

    created_at= Column(DateTime, default= datetime.utcnow)

class PaperHistory(Base):
    __tablename__= "paper_history"

    id= Column(Integer, primary_key= True, index= True)
    user_id= Column(Integer, ForeignKey("users.id"))
    exam_name= Column(String(255))
    subject= Column(String(255))
    exam_type= Column(String(255))
    pdf_path= Column(String(255))
    created_at= Column(DateTime, default= datetime.utcnow)
