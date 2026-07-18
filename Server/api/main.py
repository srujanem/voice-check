"""
AI Shield — FastAPI Main Application
The central server for AI vs Human detection
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

from api.config import settings
from api.database import init_db
from api.routes.auth_routes import router as auth_router
from api.routes.audio_routes import router as audio_router
from api.routes.image_routes import router as image_router
from api.routes.stats_routes import router as stats_router

# ===== Startup / Shutdown =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup"""
    print("\n" + "="*60)
    print("  [AI SHIELD] SERVER STARTING")
    print("="*60)

    # Create required directories
    dirs = [
        "./database", "./data/uploads/audio", "./data/uploads/images",
        "./data/audio/human", "./data/audio/ai",
        "./data/images/human", "./data/images/ai",
        "./trained_models", "./logs"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("[OK] Directory structure created")

    # Initialize database
    await init_db()

    # Warm up ML models
    print("[*] Warming up ML inference engines...")
    from api.inference import get_voice_shield, get_pixel_guard
    get_voice_shield()
    get_pixel_guard()
    print("[OK] Inference engines ready")

    import torch
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_properties(0).name
        vram = round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 1)
        print(f"[GPU] {gpu_name} ({vram}GB VRAM) - CUDA ready!")
    else:
        print("[WARN] No GPU detected - running on CPU")

    print(f"\n[SERVER] Dashboard:   http://localhost:{settings.port}")
    print(f"[SERVER] API Docs:    http://localhost:{settings.port}/docs")
    print(f"[SERVER] ReDoc:       http://localhost:{settings.port}/redoc")
    print("="*60 + "\n")

    yield  # Server runs here

    print("\n[STOP] AI Shield Server shutting down...")


# ===== App Instance =====
app = FastAPI(
    title="AI Shield API",
    description="""
## 🛡️ AI Shield — AI vs Human Detection Platform

Detect whether audio and images are AI-generated or human-created using deep learning.

### Features
- 🎙️ **Voice Detection** — Detect AI-synthesized voices (TTS, voice cloning)
- 🖼️ **Image Detection** — Detect AI-generated images (GAN, Diffusion models)
- 🔐 **User Authentication** — JWT-based secure authentication
- 📊 **Analytics Dashboard** — Real-time detection statistics
- 🎮 **GPU Accelerated** — RTX 4050 powered inference
    """,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===== Middleware =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "https://authguard.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Routers =====
app.include_router(auth_router)
from api.routes.auth_routes import db_router
app.include_router(db_router)
app.include_router(audio_router)
app.include_router(image_router)
app.include_router(stats_router)

# ===== Static files (Frontend) =====
frontend_dir = Path("./frontend")
static_dir = Path("./frontend/static")
if frontend_dir.exists():
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory="./frontend/static"), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_dashboard():
        return FileResponse("./frontend/index.html")

# ===== Health Check =====
@app.get("/health", tags=["System"])
async def health_check():
    """Server health check"""
    import torch
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_properties(0).name if torch.cuda.is_available() else None
    }


@app.get("/api", tags=["System"])
async def api_info():
    """API information endpoint"""
    return {
        "message": "🛡️ AI Shield API is running!",
        "version": settings.app_version,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "audio_detect": "/api/audio/detect",
            "image_detect": "/api/image/detect",
            "stats": "/api/stats/overview",
            "gpu_info": "/api/stats/gpu"
        }
    }


# ===== Exception Handlers =====
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"error": "Endpoint not found", "path": str(request.url.path)})


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


# ===== Entry Point =====
if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
