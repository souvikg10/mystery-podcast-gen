"""content module."""
"""
API routes for content processing and generation.
"""
import json
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.dependencies import get_current_user
from app.models.content import ContentCategory, ContentUploadRequest, AudioGenerationRequest, TranscriptRefinementRequest
from app.services.content.processing import process_files, process_urls
from app.services.audio.tts import generate_audio_segments, stream_audio_segments
from app.services.ai.gemini import refine_transcript

router = APIRouter()

@router.post("/upload")
async def upload_content(request: Request, user: dict = Depends(get_current_user)):
    """Handle multiple files or URLs upload."""
    try:
        # Get content type from request
        content_type = request.headers.get('content-type', '')
        
        if 'multipart/form-data' in content_type:
            # Handle PDF files
            form = await request.form()
            files = form.getlist('files')
            
            # Process all PDF files
            transcript = await process_files(files)
            
        else:
            # Handle URLs
            json_data = await request.json()
            data = ContentUploadRequest(**json_data)
            
            # Process all URLs
            transcript = await process_urls(data.urls)
        
        return JSONResponse({
            "message": "Content processed successfully",
            "transcript": transcript
        })
        
    except Exception as e:
        print(f"Error in upload_content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-audio")
async def generate_podcast(request: AudioGenerationRequest, user: dict = Depends(get_current_user)):
    """Generate audio from transcript."""
    try:
        transcript = request.transcript
        
        if not transcript:
            raise HTTPException(status_code=400, detail="Transcript is required")
        
        # Generate audio segments and timing data
        audio_segments, timing_data = await generate_audio_segments(transcript)
        
        # Create a streaming response
        return StreamingResponse(
            stream_audio_segments(audio_segments),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=podcast.mp3",
                "X-Timing-Data": json.dumps(timing_data)
            }
        )
        
    except Exception as e:
        print(f"Error generating podcast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refine-transcript")
async def refine_transcript_endpoint(request: TranscriptRefinementRequest, user: dict = Depends(get_current_user)):
    """Refine transcript based on notes."""
    try:
        transcript = request.transcript
        refinement_notes = request.refinement_notes
        
        if not transcript or not refinement_notes:
            raise HTTPException(status_code=400, detail="Missing transcript or refinement notes")
        
        # Refine transcript
        refined_transcript = refine_transcript(transcript, refinement_notes)
        
        return JSONResponse({
            "message": "Transcript refined successfully",
            "transcript": refined_transcript
        })
        
    except Exception as e:
        print(f"Error refining transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))