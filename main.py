from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import google.generativeai as genai
import openai
import PyPDF2
import io
import os
from pathlib import Path
from datetime import datetime
import re
import asyncio

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
model = genai.GenerativeModel('gemini-pro')

def extract_pdf_content(pdf_path: Path) -> str:
    """Extract text content from PDF file."""
    content = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting PDF content: {str(e)}")

def get_content_from_gemini(pdf_content: str) -> str:
    """Use Gemini to process and structure the PDF content."""
    prompt = """
    Please read and analyze the following content. Provide an in-depth analysis of the content.
    Make it understandable in simple concepts and entertaining. The content should be revised to make it clear and understandable and fun to read.

    This content is to used to generate an intriguing transcript later.

    Content:
    {content}
    """
    
    try:
        response = model.generate_content(prompt.format(content=pdf_content))
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing with Gemini: {str(e)}")

def generate_podcast_script(content: str) -> str:
    """Generate a two-speaker mystery style script using Gemini."""
    prompt = """
    Transform the following content into an engaging two-speaker mystery style podcast script.
    Make it intriguing and dramatic. Include interuptions and contradictions. Make it sound very intriguing.
    Format each speaker line with '**Speaker 1:**' or '**Speaker 2:**'
    

    Content to transform:
    {content}
    """
    
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

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Handle PDF upload and processing."""
    print(f"Received file: {file.filename}") 
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = file.filename.rsplit('.', 1)[0]
        safe_filename = f"{base_filename}_{timestamp}.pdf"
        pdf_path = DOCS_DIR / safe_filename
        
        # Save PDF file
        with open(pdf_path, "wb") as pdf_file:
            content = await file.read()
            pdf_file.write(content)
        
        # Extract content from PDF
        pdf_content = extract_pdf_content(pdf_path)
        # Process with Gemini
        processed_content = get_content_from_gemini(pdf_content)
        # Save processed content
        content_filename = f"{base_filename}_{timestamp}.txt"
        content_path = EXTRACTED_CONTENT_DIR / content_filename
        with open(content_path, "w", encoding="utf-8") as content_file:
            content_file.write(processed_content)
        
        # Generate podcast script
        podcast_script = generate_podcast_script(processed_content)
        script_filename = f"{base_filename}_{timestamp}.txt"
        script_path = TRANSCRIPT_CONTENT_DIR / script_filename
        with open(script_path, "w", encoding="utf-8") as script_file:
            script_file.write(podcast_script)
        return JSONResponse(content={
            "message": "PDF processed successfully",
            "filename": safe_filename,
            "transcript": podcast_script
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)