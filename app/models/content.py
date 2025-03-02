"""content module."""
"""
Models for content processing.
"""
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from enum import Enum

class ContentCategory(str, Enum):
    """Categories of content for processing."""
    RESEARCH = "research"
    TECHNICAL = "technical"

class ContentUploadRequest(BaseModel):
    """Request body for URL content processing."""
    urls: List[HttpUrl]

class ContentProcessingResponse(BaseModel):
    """Response for content processing."""
    message: str
    transcript: str

class TranscriptRefinementRequest(BaseModel):
    """Request body for transcript refinement."""
    transcript: str
    refinement_notes: str

class AudioGenerationRequest(BaseModel):
    """Request body for audio generation."""
    transcript: str

class AudioSegment(BaseModel):
    """Data for an audio segment."""
    speaker: str
    voice_id: str
    text: str
    tone: Optional[str] = None

class TimingData(BaseModel):
    """Timing data for audio segments."""
    start: float
    end: float
    speaker: str
    text: str
    tone: Optional[str] = None