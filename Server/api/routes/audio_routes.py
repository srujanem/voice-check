"""
Audio Detection Router — /api/audio/*
Handles: upload + detect, history, feedback
"""
import os
import uuid
import json
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import aiofiles

from api.database import get_db
from api.db_models import User, Upload, Detection, DetectionType, PredictionLabel
from api.schemas import DetectionResult, FeedbackCreate, FeedbackResponse, DetectionResponse
from api.auth import get_current_user
from api.config import settings
from api.inference import get_voice_shield, get_prediction_label

router = APIRouter(prefix="/api/audio", tags=["Audio Detection"])

# Ensure upload directory
AUDIO_UPLOAD_DIR = Path(settings.upload_dir) / "audio"
AUDIO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/detect", response_model=DetectionResult)
async def detect_audio(
    request: Request,
    file: UploadFile = File(..., description="Audio file (.wav, .mp3, .ogg, .flac, .m4a)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎙️ Detect if an audio file is AI-generated or Human voice.
    
    - Accepts: .wav, .mp3, .ogg, .flac, .m4a
    - Returns: prediction with confidence score
    - No login required (anonymous detection supported)
    """
    # Validate file extension
    suffix = Path(file.filename).suffix.lower()
    if suffix not in settings.allowed_audio_ext_list:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{suffix}'. Allowed: {settings.allowed_audio_ext_list}"
        )

    # Check file size
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(status_code=413, detail=f"File too large. Max {settings.max_upload_size_mb}MB")

    # Save file
    stored_name = f"{uuid.uuid4()}{suffix}"
    file_path = AUDIO_UPLOAD_DIR / stored_name
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Record upload in DB
    upload = Upload(
        user_id=current_user.id if current_user else None,
        original_filename=file.filename,
        stored_filename=stored_name,
        file_path=str(file_path),
        file_size_bytes=len(content),
        file_type=DetectionType.AUDIO,
        mime_type=file.content_type,
        upload_ip=request.client.host if request.client else "unknown"
    )
    db.add(upload)
    await db.flush()

    # Run ML inference
    voice_shield = get_voice_shield()
    result = voice_shield.predict(str(file_path))

    ai_prob = result["ai_probability"]
    human_prob = result["human_probability"]
    confidence = result["confidence"]
    pred_enum, label_text, label_color = get_prediction_label(
        ai_prob, settings.audio_confidence_threshold
    )

    # Record detection in DB
    detection = Detection(
        user_id=current_user.id if current_user else None,
        upload_id=upload.id,
        detection_type=DetectionType.AUDIO,
        prediction=PredictionLabel[pred_enum.upper()],
        confidence=confidence,
        ai_probability=ai_prob,
        human_probability=human_prob,
        model_version=result["model_version"],
        processing_time_ms=result["processing_time_ms"],
        features_extracted=json.dumps({"device": result.get("device_used", "unknown")})
    )
    db.add(detection)
    await db.flush()

    return DetectionResult(
        upload_id=upload.id,
        detection_id=detection.id,
        filename=file.filename,
        detection_type="audio",
        prediction=pred_enum,
        confidence=confidence,
        ai_probability=ai_prob,
        human_probability=human_prob,
        label=label_text,
        label_color=label_color,
        confidence_bar_width=int(confidence * 100),
        model_version=result["model_version"],
        processing_time_ms=result["processing_time_ms"],
        message=f"Analysis complete: {label_text} detected with {confidence*100:.1f}% confidence"
    )


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit feedback on a detection result to improve the model"""
    result = await db.execute(
        select(Detection).where(
            Detection.id == feedback.detection_id,
            Detection.detection_type == DetectionType.AUDIO
        )
    )
    detection = result.scalar_one_or_none()
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")

    detection.is_correct_feedback = feedback.is_correct
    detection.feedback_notes = feedback.notes
    await db.flush()

    return FeedbackResponse(message="Feedback recorded. Thank you!", detection_id=feedback.detection_id)


@router.get("/history", response_model=list[DetectionResponse])
async def get_audio_history(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audio detection history for current user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Login required for history")
    
    result = await db.execute(
        select(Detection)
        .where(Detection.user_id == current_user.id, Detection.detection_type == DetectionType.AUDIO)
        .order_by(Detection.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
