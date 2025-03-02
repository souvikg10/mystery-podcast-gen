"""episodes module."""
"""
API routes for episode management.
"""
import uuid
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional

from app.db.supabase import supabase_client
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/episodes/{project_id}")
async def get_project_episodes(project_id: str, user: dict = Depends(get_current_user)):
    """Get all episodes for a project."""
    try:
        # Verify user has access to project through organization
        user_id = user.user.id
        
        profile_response = supabase_client.table('user_profiles')\
            .select("organization_id")\
            .eq('user_id', user_id)\
            .execute()
            
        if not profile_response.data:
            raise HTTPException(status_code=403, detail="Access denied")
            
        organization_id = profile_response.data[0]['organization_id']
        
        # Check if project belongs to user's organization
        project_response = supabase_client.table('projects')\
            .select("organization_id")\
            .eq('id', project_id)\
            .execute()
            
        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found")
            
        if project_response.data[0]['organization_id'] != organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get episodes for this project
        response = supabase_client.table('episodes')\
            .select("*")\
            .eq('project_id', project_id)\
            .order('created_at', desc=True)\
            .execute()
        
        return JSONResponse({
            "status": "success",
            "data": response.data
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-episode")
async def save_episode(
    audio: UploadFile = File(...),
    project_id: str = Form(...),
    transcript: str = Form(...),
    title: Optional[str] = Form(None),
    user: dict = Depends(get_current_user)
):
    """Save a new episode."""
    try:
        # Verify user has access to project through organization
        user_id = user.user.id
        
        profile_response = supabase_client.table('user_profiles')\
            .select("organization_id")\
            .eq('user_id', user_id)\
            .execute()
            
        if not profile_response.data:
            raise HTTPException(status_code=403, detail="Access denied")
            
        organization_id = profile_response.data[0]['organization_id']
        
        # Check if project belongs to user's organization
        project_response = supabase_client.table('projects')\
            .select("organization_id")\
            .eq('id', project_id)\
            .execute()
            
        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found")
            
        if project_response.data[0]['organization_id'] != organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Generate unique filename for audio
        audio_filename = f"{uuid.uuid4()}.mp3"
        
        # Read audio file content
        audio_content = await audio.read()
        
        # Upload to Supabase Storage
        storage_response = supabase_client.storage.from_('episodes').upload(
            path=audio_filename,
            file=audio_content,
            file_options={"content-type": "audio/mpeg"}
        )
        
        if not storage_response:
            raise HTTPException(status_code=500, detail="Failed to upload audio file")
            
        # Get the public URL for the audio file
        audio_url = supabase_client.storage.from_('episodes').get_public_url(audio_filename)
            
        # Save to episodes table
        episode_data = {
            "project_id": project_id,
            "title": title or f"Episode {uuid.uuid4().hex[:8]}",
            "transcript": transcript,
            "audio_url": audio_url,
            "created_at": "now()"
        }
        
        # Insert episode into database
        episode_response = supabase_client.table('episodes').insert(episode_data).execute()
        
        if not episode_response.data:
            # Clean up the uploaded file if database insertion fails
            supabase_client.storage.from_('episodes').remove([audio_filename])
            raise HTTPException(status_code=500, detail="Failed to save episode")
            
        # Update episodes count in projects table
        project_response = supabase_client.table('projects').select("episodes_count").eq('id', project_id).execute()
        
        if project_response.data:
            current_count = project_response.data[0].get('episodes_count', 0)
            supabase_client.table('projects').update({
                "episodes_count": current_count + 1
            }).eq('id', project_id).execute()
        
        return JSONResponse({
            "status": "success",
            "message": "Episode saved successfully",
            "data": episode_response.data[0]
        })
        
    except HTTPException:
        raise
    except Exception as e:
        # If we have a filename and an error occurred after upload, clean up the file
        if 'audio_filename' in locals() and 'storage_response' in locals():
            try:
                supabase_client.storage.from_('episodes').remove([audio_filename])
            except:
                pass
        print(f"Error saving episode: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update-episode/{episode_id}")
async def update_episode(
    episode_id: str,
    audio: UploadFile = File(...),
    project_id: str = Form(...),
    transcript: str = Form(...),
    user: dict = Depends(get_current_user)
):
    """Update an existing episode."""
    try:
        # Verify user has access to project through organization
        user_id = user.user.id
        
        profile_response = supabase_client.table('user_profiles')\
            .select("organization_id")\
            .eq('user_id', user_id)\
            .execute()
            
        if not profile_response.data:
            raise HTTPException(status_code=403, detail="Access denied")
            
        organization_id = profile_response.data[0]['organization_id']
        
        # Check if project belongs to user's organization
        project_response = supabase_client.table('projects')\
            .select("organization_id")\
            .eq('id', project_id)\
            .execute()
            
        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found")
            
        if project_response.data[0]['organization_id'] != organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Read audio file content
        audio_content = await audio.read()
        
        # Generate unique filename for new audio
        audio_filename = f"{uuid.uuid4()}.mp3"
        
        # Upload new audio to Supabase Storage
        storage_response = supabase_client.storage.from_('episodes').upload(
            path=audio_filename,
            file=audio_content,
            file_options={"content-type": "audio/mpeg"}
        )
        
        if not storage_response:
            raise HTTPException(status_code=500, detail="Failed to upload audio file")
            
        # Get the public URL for the new audio file
        audio_url = supabase_client.storage.from_('episodes').get_public_url(audio_filename)
        
        # Get the current episode to find its old audio file
        old_episode = supabase_client.table('episodes').select('audio_url').eq('id', episode_id).execute()
        
        if old_episode.data:
            # Extract old filename from URL
            old_filename = old_episode.data[0]['audio_url'].split('/')[-1]
            # Delete old audio file
            try:
                supabase_client.storage.from_('episodes').remove([old_filename])
            except:
                print(f"Failed to delete old audio file: {old_filename}")
        
        # Update episode in database
        episode_data = {
            "project_id": project_id,
            "transcript": transcript,
            "audio_url": audio_url,
            "updated_at": "now()"
        }
        
        # Update episode
        episode_response = supabase_client.table('episodes').update(episode_data).eq('id', episode_id).execute()
        
        if not episode_response.data:
            # Clean up the uploaded file if database update fails
            supabase_client.storage.from_('episodes').remove([audio_filename])
            raise HTTPException(status_code=500, detail="Failed to update episode")
        
        return JSONResponse({
            "status": "success",
            "message": "Episode updated successfully",
            "data": episode_response.data[0]
        })
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up the new audio file if it was uploaded
        if 'audio_filename' in locals() and 'storage_response' in locals():
            try:
                supabase_client.storage.from_('episodes').remove([audio_filename])
            except:
                pass
        print(f"Error updating episode: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/episodes/{episode_id}")
async def delete_episode(episode_id: str, user: dict = Depends(get_current_user)):
    """Delete an episode."""
    try:
        # Get the episode to check ownership and get audio URL
        episode_response = supabase_client.table('episodes').select('project_id,audio_url').eq('id', episode_id).execute()
        
        if not episode_response.data:
            raise HTTPException(status_code=404, detail="Episode not found")
            
        project_id = episode_response.data[0]['project_id']
        audio_url = episode_response.data[0]['audio_url']
        
        # Verify user has access to project through organization
        user_id = user.user.id
        
        profile_response = supabase_client.table('user_profiles')\
            .select("organization_id")\
            .eq('user_id', user_id)\
            .execute()
            
        if not profile_response.data:
            raise HTTPException(status_code=403, detail="Access denied")
            
        organization_id = profile_response.data[0]['organization_id']
        
        # Check if project belongs to user's organization
        project_response = supabase_client.table('projects')\
            .select("organization_id")\
            .eq('id', project_id)\
            .execute()
            
        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found")
            
        if project_response.data[0]['organization_id'] != organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete the episode
        delete_response = supabase_client.table('episodes').delete().eq('id', episode_id).execute()
        
        if not delete_response.data:
            raise HTTPException(status_code=404, detail="Episode not found")
        
        # Delete the audio file
        if audio_url:
            try:
                # Extract filename from URL
                filename = audio_url.split('/')[-1]
                supabase_client.storage.from_('episodes').remove([filename])
            except Exception as e:
                print(f"Failed to delete audio file: {str(e)}")
        
        # Update episodes count in projects table
        project_response = supabase_client.table('projects').select("episodes_count").eq('id', project_id).execute()
        
        if project_response.data:
            current_count = max(0, project_response.data[0].get('episodes_count', 0) - 1)
            supabase_client.table('projects').update({
                "episodes_count": current_count
            }).eq('id', project_id).execute()
        
        return JSONResponse({
            "status": "success",
            "message": "Episode deleted successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting episode: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))