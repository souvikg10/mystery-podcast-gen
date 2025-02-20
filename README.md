# PDF to Podcast Generator

An interactive web application that converts PDF documents into engaging, two-speaker podcasts using AI. The application processes the PDF content, generates a dramatic script, and creates an audio podcast with different voices for each speaker using OpenAI's Text-to-Speech.

## Features

- 📄 PDF Upload and Processing
- 🤖 AI-powered content transformation using Google's Gemini
- 🎭 Two-speaker dramatic script generation
- 🎙️ Text-to-Speech conversion using OpenAI's TTS API
- 🎧 Built-in audio player

## Technologies Used

- Frontend:
  - HTMX for dynamic interactions
  - Tailwind CSS for styling
  - Lucide icons
  - Vanilla JavaScript

- Backend:
  - FastAPI
  - Google Gemini API for content processing
  - OpenAI API for text-to-speech
  - PyPDF2 for PDF processing

## Prerequisites

- Python 3.8+
- Google Gemini API key
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pdf-to-podcast
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment variables:
```env
export GOOGLE_API_KEY=your_gemini_api_key
export OPENAI_API_KEY=your_openai_api_key
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## Usage

1. **Upload PDF**: Click "Choose PDF" to upload your document.

2. **Review Transcript**: Once processed, you'll see the generated script with two speakers.
   - Each speaker's dialogue is color-coded
   - You can edit the text if needed
   - Tone indicators are preserved

3. **Generate Podcast**: Click "Generate Podcast" to create the audio version.
   - Uses OpenAI's diverse voice models
   - Built-in audio player for immediate playback

## Project Structure

```
pdf-to-podcast/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── static/             # Static files
│   └── index.html      # Frontend interface
├── docs/               # Uploaded PDFs
└── extracted_content/  # Processed content
```

## API Endpoints

- `GET /`: Serves the main application interface
- `POST /upload`: Handles PDF upload and processing
- `POST /generate-podcast`: Generates audio from transcript

## Environment Variables

- `GOOGLE_API_KEY`: Your Google Gemini API key
- `OPENAI_API_KEY`: Your OpenAI API key

## Development

For development mode with auto-reload:
```bash
uvicorn main:app --reload --port 8000 --log-level debug
```

## Requirements

```
fastapi==0.104.1
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
google-generativeai==0.3.0
PyPDF2==3.0.1
python-dotenv==1.0.0
jinja2==3.1.2
aiofiles==23.2.1
openai
python-dotenv==1.0.0
```

## Error Handling

The application includes comprehensive error handling for:
- Invalid file types
- API failures
- Processing errors
- File system operations

Note: This project uses external APIs (Google Gemini and OpenAI) which have their own pricing terms and usage limits.