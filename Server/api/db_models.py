"""
Database Models — SQLAlchemy ORM definitions
Tables: users, detections, uploads, model_versions
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, Text, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
import enum
from api.database import Base


class DetectionType(str, enum.Enum):
    AUDIO = "audio"
    IMAGE = "image"


class PredictionLabel(str, enum.Enum):
    AI_GENERATED = "ai_generated"
    HUMAN = "human"
    UNCERTAIN = "uncertain"


# =================== USER ===================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    detections = relationship("Detection", back_populates="user")
    uploads = relationship("Upload", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


# =================== UPLOAD ===================
class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer)
    file_type = Column(Enum(DetectionType), nullable=False)
    mime_type = Column(String(100))
    upload_ip = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="uploads")
    detection = relationship("Detection", back_populates="upload", uselist=False)

    def __repr__(self):
        return f"<Upload(id={self.id}, filename='{self.original_filename}')>"


# =================== DETECTION ===================
class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)

    detection_type = Column(Enum(DetectionType), nullable=False)
    prediction = Column(Enum(PredictionLabel), nullable=False)
    confidence = Column(Float, nullable=False)
    ai_probability = Column(Float, nullable=False)
    human_probability = Column(Float, nullable=False)

    model_version = Column(String(50), default="v1.0.0")
    processing_time_ms = Column(Float)
    features_extracted = Column(Text)  # JSON string of features

    is_correct_feedback = Column(Boolean, nullable=True)  # User feedback
    feedback_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="detections")
    upload = relationship("Upload", back_populates="detection")

    def __repr__(self):
        return f"<Detection(id={self.id}, type='{self.detection_type}', pred='{self.prediction}', conf={self.confidence:.2f})>"


# =================== MODEL VERSION ===================
class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(Enum(DetectionType), nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(Text)
    accuracy = Column(Float)
    f1_score = Column(Float)
    checkpoint_path = Column(String(500))
    is_active = Column(Boolean, default=False)
    training_epochs = Column(Integer)
    training_samples = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ModelVersion(type='{self.model_type}', version='{self.version}', acc={self.accuracy})>"


# =================== TRAINING RUN ===================
class TrainingRun(Base):
    __tablename__ = "training_runs"

    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(Enum(DetectionType), nullable=False)
    run_name = Column(String(100), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    config = Column(Text)  # JSON string
    metrics = Column(Text)  # JSON string with epoch metrics
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TrainingRun(id={self.id}, name='{self.run_name}', status='{self.status}')>"
