"""
Database configuration and schema setup for the tender extraction system.
"""

from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tender_extraction.db")

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

class ProcessingResult(Base):
    """Model for storing document processing results."""
    __tablename__ = "processing_results"
    
    document_id = Column(String(100), primary_key=True)
    processing_status = Column(String(20), nullable=False, default="pending")
    extracted_data = Column(Text)
    confidence_score = Column(Float)
    processing_time = Column(Float, nullable=False)
    error_message = Column(Text)
    retry_count = Column(Integer, nullable=False, default=0)
    validation_errors = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class GroundTruthData(Base):
    """Model for storing ground truth data for evaluation."""
    __tablename__ = "ground_truth_data"
    
    document_id = Column(String(100), ForeignKey("processing_results.document_id"), primary_key=True)
    reference_data = Column(Text, nullable=False)
    evaluation_metrics = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship
    processing_result = relationship("ProcessingResult", back_populates="ground_truth")

# Add relationship to ProcessingResult
ProcessingResult.ground_truth = relationship("GroundTruthData", back_populates="processing_result", uselist=False)

def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
