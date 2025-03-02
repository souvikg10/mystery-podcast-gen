"""
Main application entry point for the podcast generator application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.config.settings import settings
from app.api.routes import auth, projects, episodes, content, health
from app.core.exceptions import configure_exception_handlers

# Create FastAPI application
app = FastAPI(title="Podcast Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure exception handlers
configure_exception_handlers(app)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(projects.router, tags=["Projects"])
app.include_router(episodes.router, tags=["Episodes"])
app.include_router(content.router, tags=["Content"])
app.include_router(health.router, tags=["Health"])

# Set up directories
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Create static directory if it doesn't exist
STATIC_DIR.mkdir(exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# HTML Routes
@app.get("/")
async def read_root():
    """Serve the index.html page from static directory."""
    return FileResponse(STATIC_DIR / 'index.html')

@app.get("/login")
async def read_login():
    """Serve the login.html page from static directory."""
    return FileResponse(STATIC_DIR / 'login.html')

@app.get("/bridge")
async def read_bridge():
    """Serve the bridge.html page from static directory."""
    return FileResponse(STATIC_DIR / 'bridge.html')

@app.get("/app")
async def read_app():
    """Serve the app.html page from static directory."""
    return FileResponse(STATIC_DIR / 'app.html')

# Catch-all route for other HTML files
@app.get("/{filename}.html")
async def read_html(filename: str):
    """Serve HTML files from static directory."""
    file_path = STATIC_DIR / f"{filename}.html"
    if file_path.exists():
        return FileResponse(file_path)
    return {"error": "File not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)