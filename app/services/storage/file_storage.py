"""file_storage module."""
"""
File storage service for handling upload and retrieval.
"""
import uuid
from typing import Optional

from fastapi import UploadFile, HTTPException
from app.db.supabase import supabase_client

async def upload_file(file: UploadFile, bucket: str, prefix: str = "") -> str:
    """
    Upload a file to storage.
    
    Args:
        file: The file to upload.
        bucket: The storage bucket.
        prefix: Optional prefix for the filename.
        
    Returns:
        The public URL of the uploaded file.
        
    Raises:
        HTTPException: If the upload fails.
    """
    try:
        # Generate unique filename
        filename = f"{prefix}_{uuid.uuid4()}{get_file_extension(file.filename)}"
        
        # Read file content
        content = await file.read()
        
        # Get content type
        content_type = file.content_type or "application/octet-stream"
        
        # Upload to Supabase Storage
        storage_response = supabase_client.storage.from_(bucket).upload(
            path=filename,
            file=content,
            file_options={"content-type": content_type}
        )
        
        if not storage_response:
            raise HTTPException(status_code=500, detail=f"Failed to upload file {file.filename}")
            
        # Get the public URL for the file
        public_url = supabase_client.storage.from_(bucket).get_public_url(filename)
        
        return public_url
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

def delete_file(url: str, bucket: str) -> bool:
    """
    Delete a file from storage.
    
    Args:
        url: The public URL of the file.
        bucket: The storage bucket.
        
    Returns:
        True if the file was deleted successfully, False otherwise.
    """
    try:
        # Extract filename from URL
        filename = url.split('/')[-1]
        
        # Delete from Supabase Storage
        supabase_client.storage.from_(bucket).remove([filename])
        
        return True
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        return False

def get_file_extension(filename: Optional[str]) -> str:
    """
    Get the file extension from a filename.
    
    Args:
        filename: The filename.
        
    Returns:
        The file extension including the dot (e.g., ".pdf").
    """
    if not filename:
        return ""
        
    # Find the last occurrence of the dot
    last_dot = filename.rfind('.')
    
    if last_dot == -1:
        return ""
        
    return filename[last_dot:]