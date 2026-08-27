from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.generation_routes import router as generation_router
from backend.database import engine
from backend.models import Base
from backend.auth import router as auth_router
from pathlib import Path

app = FastAPI()

# database_file = Path(engine.url.database)

# if database_file.exists():
#     database_file.unlink()
Base.metadata.create_all(bind=engine)

# print("DATABASE URL:", engine.url)
# print("DATABASE FILE:", engine.url.database)

app.include_router(auth_router)

app.add_middleware(     
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generation_router)

@app.get("/")
def home():
    return {"message": "AI Exam Generator Running 🚀"}