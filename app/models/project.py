"""project module."""
"""
Pydantic models for project and episode-related data.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ProjectCreate(BaseModel):
    """Data required to create a new project."""
    name: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    """Project data returned to the client."""
    id: UUID
    name: str
    description: Optional[str] = None
    organization_id: UUID
    episodes_count: int = 0
    created_at: datetime

class EpisodeCreate(BaseModel):
    """Data required to create a new episode."""
    project_id: UUID
    title: Optional[str] = None
    transcript: str

class EpisodeUpdate(BaseModel):
    """Data required to update an episode."""
    project_id: Optional[UUID] = None
    title: Optional[str] = None
    transcript: Optional[str] = None

class EpisodeResponse(BaseModel):
    """Episode data returned to the client."""
    id: UUID
    project_id: UUID
    title: str
    transcript: str
    audio_url: str
    created_at: datetime
    updated_at: Optional[datetime] = None