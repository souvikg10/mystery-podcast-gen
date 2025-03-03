"""tts module."""
"""
Text-to-speech services for generating audio from text.
"""
import os
import httpx
import tempfile
import asyncio
from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, AsyncGenerator, Optional
from io import BytesIO

from fastapi import HTTPException
from pydub import AudioSegment as PydubAudioSegment

from app.config.settings import settings
from app.models.content import AudioSegment, TimingData

class TTSProvider(ABC):
    """Abstract base class for text-to-speech providers."""
    
    @abstractmethod
    async def generate_audio_segment(self, text: str, voice_id: str) -> Tuple[bytes, float]:
        """Generate a single audio segment and return the audio bytes and duration."""
        pass

class ElevenLabsTTS(TTSProvider):
    """ElevenLabs text-to-speech provider."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = settings.ELEVENLABS_API_URL

    async def generate_audio_segment(self, text: str, voice_id: str) -> Tuple[bytes, float]:
        """
        Generate audio for a single segment using ElevenLabs REST API.
        
        Args:
            text: The text to convert to speech.
            voice_id: The voice ID to use.
            
        Returns:
            Tuple of (audio_bytes, duration_in_seconds).
            
        Raises:
            HTTPException: If there is an error generating the audio.
        """
        try:
            url = f"{self.api_url}/text-to-speech/{voice_id}/stream"
            
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers)
                
                if response.status_code != 200:
                    raise Exception(f"ElevenLabs API error: {response.text}")
                
                # Get audio duration from response headers if available
                duration = 0
                try:
                    content_length = int(response.headers.get('content-length', 0))
                    # Approximate duration based on MP3 bitrate (assuming 128kbps)
                    duration = content_length / (128 * 1024 / 8)
                except:
                    # Fallback duration estimation
                    duration = len(text.split()) * 0.3  # Rough estimate: 0.3 seconds per word
                
                return response.content, duration

        except Exception as e:
            print(f"Error generating audio segment: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

class OpenAITTS(TTSProvider):
    """OpenAI text-to-speech provider."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Voice mapping for OpenAI (alloy, echo, fable, onyx, nova, shimmer)
        self.voice_mapping = {
            "ThT5KcBeYPX3keUQqHPh": "onyx",  # Map ElevenLabs Adam to OpenAI onyx
            "ErXwobaYiN019PkySvjV": "echo"   # Map ElevenLabs Antoni to OpenAI echo
        }

    async def generate_audio_segment(self, text: str, voice_id: str) -> Tuple[bytes, float]:
        """
        Generate audio for a single segment using OpenAI TTS API.
        
        Args:
            text: The text to convert to speech.
            voice_id: The voice ID to use (will be mapped to OpenAI voice).
            
        Returns:
            Tuple of (audio_bytes, duration_in_seconds).
            
        Raises:
            HTTPException: If there is an error generating the audio.
        """
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.api_key)
            openai_voice = self.voice_mapping.get(voice_id, "alloy")
            
            response = await client.audio.speech.create(
                model="tts-1",
                voice=openai_voice,
                input=text
            )
            
            # Get the response content
            audio_data = response.content
            
            # Simple duration estimation based on word count
            duration = len(text.split()) * 0.3  # Rough estimate: 0.3 seconds per word
            
            return audio_data, duration
            
        except Exception as e:
            print(f"Error generating audio segment with OpenAI: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

def get_tts_provider() -> TTSProvider:
    """
    Factory function to get the appropriate TTS provider based on environment variable.
    
    Returns:
        A TTSProvider implementation.
        
    Raises:
        ValueError: If required API keys are missing.
    """
    voice_mode = os.getenv("VOICE_MODE", "elevenlabs").lower()
    
    if voice_mode == "openai":
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return OpenAITTS(openai_api_key)
    else:
        return ElevenLabsTTS(settings.ELEVEN_LABS_API_KEY)

async def generate_audio_segments(transcript: str) -> Tuple[List[Tuple[bytes, float]], List[Dict]]:
    """
    Generate audio segments and timing information for a transcript.
    
    Args:
        transcript: The transcript to convert to speech.
        
    Returns:
        Tuple of (audio_segments, timing_data).
        
    Raises:
        HTTPException: If there is an error generating the audio.
    """
    from app.services.content.processing import parse_transcript
    
    segments = parse_transcript(transcript)
    audio_segments = []
    timing_data = []
    current_time = 0

    # Get the appropriate TTS provider
    tts_provider = get_tts_provider()

    for segment in segments:
        try:
            # Add any tone/mood instructions to the text
            text_to_speak = segment.text
            if segment.tone:
                text_to_speak = f'[{segment.tone}] {text_to_speak}'

            # Generate audio for segment using the provider
            audio_content, duration = await tts_provider.generate_audio_segment(
                text_to_speak,
                segment.voice_id
            )
            
            # Store timing information
            timing_data.append(TimingData(
                start=current_time,
                end=current_time + duration,
                speaker=segment.speaker,
                text=segment.text,
                tone=segment.tone
            ).dict())
            
            # Update current time and store audio segment
            current_time += duration
            audio_segments.append((audio_content, duration))
            
        except Exception as e:
            print(f"Error processing segment: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

    return audio_segments, timing_data

async def stream_audio_segments(segments: List[Tuple[bytes, float]]) -> AsyncGenerator[bytes, None]:
    """
    Stream audio segments as a single continuous stream.
    
    Args:
        segments: List of audio segments as (bytes, duration) tuples.
        
    Yields:
        Audio bytes that can be streamed to the client.
    """
    for audio_content, _ in segments:
        yield audio_content

def combine_audio_segments(segments: List[bytes]) -> bytes:
    """
    Combine multiple audio segments into a single audio file.
    
    Args:
        segments: List of audio segment bytes.
        
    Returns:
        Combined audio as bytes.
        
    Raises:
        HTTPException: If there is an error combining the segments.
    """
    try:
        combined = PydubAudioSegment.empty()
        
        for audio_content in segments:
            # Convert bytes to AudioSegment
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_content)
                temp_file.flush()
                segment = PydubAudioSegment.from_mp3(temp_file.name)
                combined += segment
                os.unlink(temp_file.name)
        
        # Export to bytes
        buffer = BytesIO()
        combined.export(buffer, format='mp3')
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Error combining audio segments: {str(e)}")
        raise HTTPException(status_code=500, detail="Error combining audio segments")