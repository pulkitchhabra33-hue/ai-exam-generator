from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.generate import router as generate_router
from database import engine
from models import Base
from auth import router as auth_router

app = FastAPI()

Base.metadata.create_all(bind= engine)
app.include_router(auth_router)

app.add_middleware(     
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router)

@app.get("/")
def home():
    return {"message": "AI Exam Generator Running 🚀"}