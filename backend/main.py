from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.generate import router as generate_router

app = FastAPI()

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