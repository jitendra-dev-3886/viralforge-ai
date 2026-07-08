from fastapi import FastAPI

app = FastAPI(
    title="ViralForge AI",
    version="1.0.0",
    description="AI Content Automation Platform"
)

@app.get("/")
async def root():
    return {
        "status": "running",
        "project": "ViralForge AI",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "success": True,
        "message": "API is healthy"
    }