from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.database import Base, engine, SessionLocal
from app.services.billing_service import seed_plans
from app.api.billing import router as billing_router

from app.api.auth import router as auth_router
from app.api.ai import router as ai_router
from app.api.ai_settings import router as ai_settings_router
from app.api.trends import router as trend_router
from app.api.project import router as project_router
from app.api.brand import router as brand_router
from app.api.content import router as content_router
from app.api.media import router as media_router
from app.api.scene import router as scene_router
from app.api.downloader import router as downloader_router
from app.api.voice import router as voice_router
from app.api.render import router as render_router
from app.api.subtitle import router as subtitle_router
from app.api.project_render import router as project_render_router
from app.api.analytics import router as analytics_router
from app.api.niche import router as niche_router
from app.api.admin import router as admin_router
from app.api.schedule import router as schedule_router


from app import models


# ==========================================================
# Create Database Tables
# ==========================================================

Base.metadata.create_all(bind=engine)
with SessionLocal() as billing_db:
    seed_plans(billing_db)


# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(
    title="ViralForge AI API",
    version="1.0.0",
)

storage_dir = Path(__file__).resolve().parent.parent / "storage"
storage_dir.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(storage_dir)), name="storage")


# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ==========================================================
# API Routes
# ==========================================================

app.include_router(auth_router)

app.include_router(ai_router)
app.include_router(ai_settings_router)
app.include_router(billing_router)

app.include_router(trend_router)

app.include_router(project_router)

app.include_router(brand_router)

app.include_router(content_router)

app.include_router(media_router)

app.include_router(scene_router)

app.include_router(downloader_router)

app.include_router(voice_router)

app.include_router(render_router)

app.include_router(subtitle_router)
app.include_router(project_render_router)
app.include_router(analytics_router)
app.include_router(niche_router)
app.include_router(admin_router)
app.include_router(schedule_router)


# ==========================================================
# Root
# ==========================================================

@app.get("/")
def root():

    return {
        "success": True,
        "message": "Welcome to ViralForge AI API",
    }


# ==========================================================
# Health Check
# ==========================================================

@app.get("/health")
def health():

    return {
        "success": True,
        "status": "Healthy",
    }
