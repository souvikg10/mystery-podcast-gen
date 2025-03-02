"""gemini module."""
"""
Service for interacting with Google's Gemini AI.
"""
import google.generativeai as genai
from fastapi import HTTPException

from app.config.settings import settings
from app.models.content import ContentCategory
from app.services.ai.prompts import CATEGORY_PROMPTS, CONTENT_SUMMARY_PROMPT, TRANSCRIPT_REFINEMENT_PROMPT

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def generate_podcast_script(category: ContentCategory, content: str) -> str:
    """
    Generate a podcast script based on the content category.
    
    Args:
        category: The content category (research or technical).
        content: The content to transform.
        
    Returns:
        The generated podcast script.
        
    Raises:
        HTTPException: If there is an error generating the script.
    """
    prompt = CATEGORY_PROMPTS[category]
    try:
        response = model.generate_content(prompt.format(content=content))
        return response.text
    except Exception as e:
        print(f"Error generating podcast script: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating podcast script")

def generate_content_summary(content: str) -> str:
    """
    Generate a summary of combined content.
    
    Args:
        content: The content to summarize.
        
    Returns:
        The summarized content.
        
    Raises:
        HTTPException: If there is an error generating the summary.
    """
    try:
        response = model.generate_content(CONTENT_SUMMARY_PROMPT.format(content=content))
        return response.text
    except Exception as e:
        print(f"Error generating content summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating content summary")

def refine_transcript(transcript: str, refinement_notes: str) -> str:
    """
    Refine a podcast transcript based on the provided notes.
    
    Args:
        transcript: The transcript to refine.
        refinement_notes: Notes on how to refine the transcript.
        
    Returns:
        The refined transcript.
        
    Raises:
        HTTPException: If there is an error refining the transcript.
    """
    try:
        response = model.generate_content(
            TRANSCRIPT_REFINEMENT_PROMPT.format(
                transcript=transcript,
                notes=refinement_notes
            )
        )
        return response.text
    except Exception as e:
        print(f"Error refining transcript: {str(e)}")
        raise HTTPException(status_code=500, detail="Error refining transcript")