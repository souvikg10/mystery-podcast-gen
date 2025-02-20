import google.generativeai as genai
import openai
import PyPDF2
import io
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import re
import asyncio
import httpx
from bs4 import BeautifulSoup
from enum import Enum
from fastapi import FastAPI, File, HTTPException, Request, Form
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.datastructures import UploadFile

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure directories
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
EXTRACTED_CONTENT_DIR = BASE_DIR / "extracted_content"
STATIC_DIR = BASE_DIR / "static"
TRANSCRIPT_CONTENT_DIR = BASE_DIR / "transcript"

# Create necessary directories
DOCS_DIR.mkdir(exist_ok=True)
EXTRACTED_CONTENT_DIR.mkdir(exist_ok=True)
TRANSCRIPT_CONTENT_DIR.mkdir(exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

class ContentCategory(str, Enum):
    RESEARCH = "research"
    TECHNICAL = "technical"

PROMPTS = {
    ContentCategory.RESEARCH: """
    Transform this research paper into a thrilling true crime narrative podcast.
    Frame the research problem as a mystery, methods as investigation techniques,
    and findings as dramatic revelations. Use dramatic tension and create suspense
    around the research outcomes.
    The conversation is happening between two speakers. Focus only on what they will say
    No additional sound cues.
    
    Style Guidelines:
    - Present the research question as an unsolved mystery
    - Turn methodology into detective work
    - Frame data analysis as uncovering evidence
    - Present findings as breakthrough revelations
    

    Original content:
    {content}
    """,
    
    ContentCategory.TECHNICAL: """
    Transform this technical documentation into a conspiracy theory style podcast script.
    Present the technical concepts as hidden knowledge being revealed, with connections
    and patterns that "they don't want you to know about."
    The conversation is happening between two speakers. Focus only on what they will say
    No additional sound cues.
    
    Style Guidelines:
    - Frame technical concepts as "hidden knowledge"
    - Present features as "secret capabilities"
    - Connect different parts of the documentation in unexpected ways
    - Use phrases like "But here's what they're not telling you..."
    
    
    Original content:
    {content}
    """
}


def generate_podcast_script(prompt: str, content: str) -> str:
    """Generate a two-speaker mystery style script using Gemini."""
    try:
        response = model.generate_content(prompt.format(content=content))
        return response.text
    except Exception as e:
        print(f"Error generating podcast script: {str(e)}")
        return content 

@app.get("/")
async def read_root():
    """Serve the index.html page from static directory."""
    return FileResponse('static/index.html')

async def process_pdf_file(file: UploadFile) -> str:
    """Process a single PDF file and return its content."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail=f"File {file.filename} must be a PDF")
    
    try:
        content = await file.read()
        pdf = PyPDF2.PdfReader(io.BytesIO(content))
        text_content = ""
        for page in pdf.pages:
            text_content += page.extract_text() + "\n"
        return text_content
    except Exception as e:
        print(f"Error processing PDF {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF {file.filename}")

async def process_url(url: str) -> str:
    """Process a single URL and return its content."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unnecessary elements
            for element in soup.find_all(['nav', 'footer', 'script', 'style', 'header', 'aside']):
                element.decompose()
            
            # Try multiple content selectors
            content = (
                soup.find('main') or 
                soup.find('article') or 
                soup.find('div', class_=['content', 'documentation', 'docs-content']) or
                soup.find('div', id=['content', 'main-content', 'documentation'])
            )
            
            return content.get_text(separator='\n', strip=True) if content else soup.get_text(separator='\n', strip=True)
            
        except Exception as e:
            print(f"Error processing URL {url}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to process URL: {url}")

@app.post("/upload")
async def upload_content(request: Request):
    """Handle multiple files or URLs upload."""
    try:
        # Get content type from request
        content_type = request.headers.get('content-type', '')
        
        if 'multipart/form-data' in content_type:
            # Handle PDF files
            form = await request.form()
            files = form.getlist('files')
            category = ContentCategory.RESEARCH
            
            # Process all PDF files
            contents = []
            for file in files:
                if isinstance(file, UploadFile):
                    content = await process_pdf_file(file)
                    contents.append(content)
            
        else:
            # Handle URLs
            json_data = await request.json()
            urls = json_data.get('urls', [])
            category = ContentCategory.TECHNICAL
            
            # Process all URLs in parallel
            contents = await asyncio.gather(*[process_url(url) for url in urls])
        
        if not contents:
            raise HTTPException(status_code=400, detail="No content to process")
        
        # Combine all content
        combined_content = "\n\n=== Next Document ===\n\n".join(contents)
        # Process with Gemini
        processed_content = generate_content_summary(combined_content)
        
        # Generate transcript
        transcript = generate_podcast_script(category, processed_content)
        
        # Save processed content and transcript
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        content_path = EXTRACTED_CONTENT_DIR / f"combined_content_{timestamp}.txt"
        with open(content_path, "w", encoding="utf-8") as f:
            f.write(processed_content)
            
        transcript_path = TRANSCRIPT_CONTENT_DIR / f"transcript_{timestamp}.txt"
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        
        return JSONResponse({
            "message": "Content processed successfully",
            "transcript": transcript
        })
        
    except Exception as e:
        print("Error in upload_content")
        raise HTTPException(status_code=500, detail=str(e))

def generate_content_summary(content: str) -> str:
    """Generate a summary of combined content using Gemini."""
    prompt = """
    Analyze and synthesize the following content into a coherent narrative.
    Each document is separated by '=== Next Document ==='.
    Find connections between the documents and create a unified story.
    Make it clear and engaging while preserving the key information from each source.

    Content to analyze:
    {content}
    """
    
    try:
        response = model.generate_content(prompt.format(content=content))
        return response.text
    except Exception as e:
        print(f"Error generating content summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating content summary")

def generate_podcast_script(category: ContentCategory, content: str) -> str:
    """Generate a podcast script based on the category."""
    prompt = PROMPTS[category]
    try:
        response = model.generate_content(prompt.format(content=content))
        return response.text
    except Exception as e:
        print(f"Error generating podcast script: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating podcast script")


@app.post("/generate-podcast")
async def generate_podcast(request: Request):
    """Generate podcast audio from transcript."""
    try:
        # Get the transcript from request body
        data = await request.json()
        transcript = data.get('transcript')
        
        if not transcript:
            raise HTTPException(status_code=400, detail="Transcript is required")

        
        # Generate audio using text-to-speech
        audio_content = await generate_audio(transcript)
        
        # Return audio file
        return StreamingResponse(
            io.BytesIO(audio_content),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=podcast.mp3"}
        )
        
    except Exception as e:
        print("Error generating podcast")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_audio(transcript):
    """Generate audio using OpenAI's TTS API."""
    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        # Configure voices for each speaker
        voices = {
            "Speaker 1": "alloy",   # Male-sounding voice
            "Speaker 2": "nova"     # Female-sounding voice
        }

        async def generate_segment(text, speaker):
            """Generate audio for a single segment using OpenAI TTS."""
            try:
                # Generate audio using OpenAI's TTS
                response = await asyncio.to_thread(
                    client.audio.speech.create,
                    model="tts-1",
                    voice=voices[speaker],
                    input=text
                )
                
                # Read the audio content
                audio_content = await asyncio.to_thread(response.read)
                return audio_content
            except Exception as e:
                print(f"Error generating segment for {speaker}: {str(e)}")
                return None

        # Preprocess and filter segments
        def process_segment(segment):
            """Preprocess a single segment, extracting speaker and text."""
            if not segment.strip():
                return None

            # Extract speaker
            speaker_match = re.search(r'\*\*(Speaker \d):\*\*', segment)
            if not speaker_match:
                return None

            speaker = speaker_match.group(1)
            
            # Remove speaker tag and tone indicators
            text = re.sub(r'\*\*(Speaker \d):\*\*', '', segment)
            text = re.sub(r'\((.*?)\)', '', text).strip()

            return {"speaker": speaker, "text": text}

        # Split and preprocess segments
        segments = [
            process_segment(seg) 
            for seg in transcript.split('\n\n')
        ]
        
        # Filter out None values
        valid_segments = [seg for seg in segments if seg]

        # Generate audio segments in parallel
        tasks = [
            generate_segment(seg['text'], seg['speaker']) 
            for seg in valid_segments
        ]
        
        # Gather results, filtering out None values
        audio_segments = await asyncio.gather(*tasks)
        valid_audio_segments = [seg for seg in audio_segments if seg is not None]

        if not valid_audio_segments:
            raise ValueError("No valid audio segments generated")
        def concatenate_audio_bytes(segments):
            """Concatenate audio segments into a single bytes object."""
            return b''.join(segments)

        # Ensure we return a bytes-like object
        full_audio = concatenate_audio_bytes(valid_audio_segments)
        
        return full_audio
    except Exception as e:
        print(e)
        raise e

@app.post("/refine-transcript")
async def refine_transcript(request: Request):
    try:
        data = await request.json()
        transcript = data.get('transcript')
        refinement_notes = data.get('refinement_notes')
        
        if not transcript or not refinement_notes:
            raise HTTPException(status_code=400, detail="Missing transcript or refinement notes")
        
        prompt = """
        Refine the following podcast transcript according to these notes while keeping 
        the core content and information intact. Maintain the same two-speaker format 
        and dramatic elements, but adjust the style and presentation as requested.

        Original Transcript:
        {transcript}

        Refinement Notes:
        {notes}

        Keep the format:
        **Speaker 1:** (tone) dialogue
        **Speaker 2:** (tone) dialogue

        Make sure to:
        1. Keep all important information from the original
        2. Maintain the conversational flow
        3. Apply the requested style changes
        4. Keep dramatic elements and tone indicators
        5. Preserve the alternating speaker format
        """
        
        response = model.generate_content(
            prompt.format(transcript=transcript, notes=refinement_notes)
        )
        
        return JSONResponse({
            "message": "Transcript refined successfully",
            "transcript": response.text
        })
        
    except Exception as e:
        print("Error refining transcript")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)