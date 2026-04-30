from fastapi import FastAPI
from backend.routes.generate import router as generate_router

app= FastAPI()
app.include_router(generate_router)

@app.get("/")
def home():
    return {"message": "AI Exam Generator Running 🚀"}