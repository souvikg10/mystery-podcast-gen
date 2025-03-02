"""settings module."""
"""
Application configuration settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """Application settings."""
    
    # API configuration
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    
    # External APIs
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    ELEVEN_LABS_API_KEY: str = os.getenv("ELEVEN_LABS_API_KEY")
    ELEVENLABS_API_URL: str = "https://api.elevenlabs.io/v1"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    #Voice mode
    VOICE_MODE: str = os.getenv("VOICE_MODE")    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    
    
    # Voice mappings
    VOICE_MAPPINGS: dict = {
        "Speaker 1": "ThT5KcBeYPX3keUQqHPh",  # Adam
        "Speaker 2": "ErXwobaYiN019PkySvjV"   # Antoni
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create settings instance
settings = Settings()


# Validate required environment variables
if not settings.GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

if not settings.ELEVEN_LABS_API_KEY:
    raise ValueError("ELEVEN_LABS_API_KEY not found in environment variables")

if not settings.SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY not found in environment variables")

if not settings.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")