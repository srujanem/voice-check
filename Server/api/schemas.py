"""
Pydantic Schemas — Request/Response validation models
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DetectionTypeEnum(str, Enum):
    audio = "audio"
    image = "image"


class PredictionLabelEnum(str, Enum):
    ai_generated = "ai_generated"
    human = "human"
    uncertain = "uncertain"


# ===== AUTH SCHEMAS =====
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ===== DETECTION SCHEMAS =====
class DetectionResponse(BaseModel):
    id: int
    detection_type: DetectionTypeEnum
    prediction: PredictionLabelEnum
    confidence: float
    ai_probability: float
    human_probability: float
    model_version: str
    processing_time_ms: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class DetectionResult(BaseModel):
    """Immediate response from detection endpoint"""
    upload_id: int
    detection_id: int
    filename: str
    detection_type: DetectionTypeEnum
    prediction: PredictionLabelEnum
    confidence: float
    ai_probability: float
    human_probability: float
    label: str
    label_color: str
    confidence_bar_width: int
    model_version: str
    processing_time_ms: float
    message: str


class FeedbackCreate(BaseModel):
    detection_id: int
    is_correct: bool
    notes: Optional[str] = Field(None, max_length=500)


class FeedbackResponse(BaseModel):
    message: str
    detection_id: int


# ===== MODEL VERSION SCHEMAS =====
class ModelVersionResponse(BaseModel):
    id: int
    model_type: DetectionTypeEnum
    version: str
    description: Optional[str]
    accuracy: Optional[float]
    f1_score: Optional[float]
    is_active: bool
    training_epochs: Optional[int]
    training_samples: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ===== TRAINING RUN SCHEMAS =====
class TrainingStartRequest(BaseModel):
    model_type: DetectionTypeEnum
    run_name: str = Field(..., min_length=3, max_length=100)
    epochs: Optional[int] = Field(20, ge=1, le=200)
    batch_size: Optional[int] = Field(16, ge=1, le=128)
    learning_rate: Optional[float] = Field(0.0001, gt=0, lt=1)


class TrainingRunResponse(BaseModel):
    id: int
    model_type: DetectionTypeEnum
    run_name: str
    status: str
    config: Optional[str]
    metrics: Optional[str]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ===== STATS SCHEMAS =====
class SystemStats(BaseModel):
    total_detections: int
    audio_detections: int
    image_detections: int
    ai_detected: int
    human_detected: int
    avg_confidence: float
    recent_detections: List[DetectionResponse]
