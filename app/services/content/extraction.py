"""extraction module."""
"""
Services for extracting content from PDFs and URLs.
"""
import io
import PyPDF2
import httpx
from fastapi import UploadFile, HTTPException
from bs4 import BeautifulSoup

async def extract_content_from_pdf(file: UploadFile) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        file: The uploaded PDF file.
        
    Returns:
        The extracted text content.
        
    Raises:
        HTTPException: If there is an error processing the PDF.
    """
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

async def extract_content_from_url(url: str) -> str:
    """
    Extract text content from a URL.
    
    Args:
        url: The URL to extract content from.
        
    Returns:
        The extracted text content.
        
    Raises:
        HTTPException: If there is an error processing the URL.
    """
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