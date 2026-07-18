"""
Stats & Dashboard Router — /api/stats/*
Returns detection statistics and system info
"""
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from api.database import get_db
from api.db_models import Detection, DetectionType, PredictionLabel
from api.schemas import DetectionResponse
from api.config import settings

router = APIRouter(prefix="/api/stats", tags=["Statistics"])


@router.get("/config")
async def get_config():
    """Get system configuration for the dashboard"""
    return {
        "api_key": settings.api_key,
        "app_version": settings.app_version,
        "debug_mode": settings.debug
    }


@router.get("/overview")
async def get_overview(db: AsyncSession = Depends(get_db)):
    """Get system-wide detection statistics"""
    total = await db.scalar(select(func.count(Detection.id)))
    audio_count = await db.scalar(
        select(func.count(Detection.id)).where(Detection.detection_type == DetectionType.AUDIO)
    )
    image_count = await db.scalar(
        select(func.count(Detection.id)).where(Detection.detection_type == DetectionType.IMAGE)
    )
    ai_count = await db.scalar(
        select(func.count(Detection.id)).where(Detection.prediction == PredictionLabel.AI_GENERATED)
    )
    human_count = await db.scalar(
        select(func.count(Detection.id)).where(Detection.prediction == PredictionLabel.HUMAN)
    )
    avg_conf_result = await db.scalar(select(func.avg(Detection.confidence)))
    avg_confidence = round(float(avg_conf_result or 0), 4)

    recent_result = await db.execute(
        select(Detection).order_by(Detection.created_at.desc()).limit(5)
    )
    recent = recent_result.scalars().all()

    return {
        "total_detections": total or 0,
        "audio_detections": audio_count or 0,
        "image_detections": image_count or 0,
        "ai_detected": ai_count or 0,
        "human_detected": human_count or 0,
        "avg_confidence": avg_confidence,
        "recent_detections": [DetectionResponse.model_validate(d) for d in recent]
    }


@router.get("/gpu")
async def get_gpu_info():
    """Get GPU and CUDA information"""
    if not TORCH_AVAILABLE:
        return {
            "cuda_available": False,
            "device_count": 0,
            "note": "PyTorch not installed yet — install with: pip install torch --index-url https://download.pytorch.org/whl/cu128"
        }

    info = {
        "cuda_available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
    }
    if torch.cuda.is_available():
        props = torch.cuda.get_device_properties(0)
        info.update({
            "device_name": props.name,
            "total_memory_gb": round(props.total_memory / 1024**3, 2),
            "memory_allocated_gb": round(torch.cuda.memory_allocated(0) / 1024**3, 4),
            "memory_reserved_gb": round(torch.cuda.memory_reserved(0) / 1024**3, 4),
            "cuda_version": torch.version.cuda,
            "pytorch_version": torch.__version__,
            "compute_capability": f"{props.major}.{props.minor}"
        })
    return info
