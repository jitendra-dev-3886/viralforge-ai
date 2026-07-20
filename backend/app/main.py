from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.api.auth import router as auth_router
from app.api.ai import router as ai_router
from app.api.trends import router as trend_router
from app.api.project import router as project_router
from app.api.media import router as media_router
from app.api.brand import router as brand_router
from app.api.content import router as content_router
from app.api.media import router as media_router


from app import models

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ViralForge AI API",
    version="1.0.0",
)

# ==========================
# CORS
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ==========================
# API Routes
# ==========================
app.include_router(auth_router)
app.include_router(ai_router)
app.include_router(trend_router)
app.include_router(project_router)
app.include_router(media_router)
app.include_router(brand_router)
app.include_router(content_router)
app.include_router(media_router)
# ==========================
# Root
# ==========================
@app.get("/")
def root():
    return {
        "success": True,
        "message": "Welcome to ViralForge AI API",
    }

# ==========================
# Health Check
# ==========================
@app.get("/health")
def health():
    return {
        "success": True,
        "status": "Healthy",
    }