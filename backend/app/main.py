from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.api.auth import router as auth_router

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ViralForge AI API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "success": True,
        "message": "Welcome to ViralForge AI API",
    }


@app.get("/health")
def health():
    return {
        "success": True,
        "status": "Healthy",
    }