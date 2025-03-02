"""processing module."""
"""
Services for processing and transforming content.
"""
import asyncio
import re
from typing import List, Dict, Tuple
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile, HTTPException

from app.config.settings import settings
from app.models.content import ContentCategory, AudioSegment
from app.services.content.extraction import extract_content_from_pdf, extract_content_from_url
from app.services.ai.gemini import generate_content_summary, generate_podcast_script, refine_transcript

async def process_files(files: List[UploadFile]) -> str:
    """
    Process multiple PDF files and return a combined transcript.
    
    Args:
        files: List of uploaded PDF files.
        
    Returns:
        The generated transcript.
    """
    # Process all PDF files
    contents = []
    for file in files:
        content = await extract_content_from_pdf(file)
        contents.append(content)
    
    if not contents:
        raise HTTPException(status_code=400, detail="No content to process")
    
    # Combine and process content
    return await process_combined_content(contents, ContentCategory.RESEARCH)

async def process_urls(urls: List[str]) -> str:
    """
    Process multiple URLs and return a combined transcript.
    
    Args:
        urls: List of URLs to process.
        
    Returns:
        The generated transcript.
    """
    # Process all URLs in parallel
    contents = await asyncio.gather(*[extract_content_from_url(url) for url in urls])
    
    if not contents:
        raise HTTPException(status_code=400, detail="No content to process")
    
    # Combine and process content
    return await process_combined_content(contents, ContentCategory.TECHNICAL)

async def process_combined_content(contents: List[str], category: ContentCategory) -> str:
    """
    Process combined content and generate a transcript.
    
    Args:
        contents: List of content strings.
        category: The content category.
        
    Returns:
        The generated transcript.
    """
    # Combine all content
    combined_content = "\n\n=== Next Document ===\n\n".join(contents)
    
    # Process with AI
    processed_content = generate_content_summary(combined_content)
    
    # Generate transcript
    transcript = generate_podcast_script(category, processed_content)
    
    # Save processed content and transcript
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    content_path = settings.EXTRACTED_CONTENT_DIR / f"combined_content_{timestamp}.txt"
    with open(content_path, "w", encoding="utf-8") as f:
        f.write(processed_content)
        
    transcript_path = settings.TRANSCRIPT_CONTENT_DIR / f"transcript_{timestamp}.txt"
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    
    return transcript

def parse_transcript(transcript: str) -> List[AudioSegment]:
    """
    Parse transcript into segments with speaker and tone information.
    
    Args:
        transcript: The transcript to parse.
        
    Returns:
        List of AudioSegment objects.
    """
    segments = []
    pattern = r'\*\*(Speaker \d):\*\*\s*(?:\((.*?)\))?\s*(.+)'
    
    for line in transcript.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        match = re.match(pattern, line)
        if match:
            speaker, tone, text = match.groups()
            
            # Get voice ID for speaker
            voice_id = settings.VOICE_MAPPINGS.get(speaker)
            if not voice_id:
                continue
                
            segments.append(AudioSegment(
                speaker=speaker,
                voice_id=voice_id,
                text=text.strip(),
                tone=tone
            ))
    
    return segments