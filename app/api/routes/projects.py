"""projects module."""
"""
API routes for project management.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.db.supabase import supabase_client
from app.models.project import ProjectCreate, ProjectResponse
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/user-projects")
async def get_user_projects(user: dict = Depends(get_current_user)):
    """Get the user's organization and projects."""
    try:
        # Get user ID from the authenticated user
        user_id = user.user.id
        
        # Get user's profile to find their organization
        profile_response = supabase_client.table('user_profiles')\
            .select("organization_id")\
            .eq('user_id', user_id)\
            .execute()
            
        if not profile_response.data:
            return JSONResponse({
                "status": "success",
                "organization": None,
                "projects": []
            })
        
        organization_id = profile_response.data[0]['organization_id']
            
        # Get organization details
        org_response = supabase_client.table('organizations')\
            .select("*")\
            .eq('id', organization_id)\
            .execute()
            
        # Get projects for this organization
        projects_response = supabase_client.table('projects')\
            .select("*")\
            .eq('organization_id', organization_id)\
            .execute()
            
        return JSONResponse({
            "status": "success",
            "organization": org_response.data[0] if org_response.data else None,
            "projects": projects_response.data
        })
    except Exception as e:
        print(f"Error getting user projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-project")
async def create_project(project: ProjectCreate, user: dict = Depends(get_current_user)):
    """Create a new project for the user's organization."""
    try:
        # Get user's organization ID
        user_id = user.user.id
        
        profile_response = supabase_client.table('user_profiles')\
            .select("organization_id")\
            .eq('user_id', user_id)\
            .execute()
            
        if not profile_response.data or not profile_response.data[0]['organization_id']:
            raise HTTPException(status_code=400, detail="User doesn't have an organization")
            
        organization_id = profile_response.data[0]['organization_id']
        
        # Insert new project with the organization ID
        response = supabase_client.table('projects').insert({
            "name": project.name,
            "description": project.description,
            "organization_id": organization_id,
            "episodes_count": 0,
            "created_at": "now()"
        }).execute()
        
        return JSONResponse({
            "status": "success",
            "data": response.data[0]
        })
    except Exception as e:
        print(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-project/{project_id}")
async def delete_project(project_id: str, user: dict = Depends(get_current_user)):
    """Delete a project."""
    try:
        # Check if user has access to this project
        user_id = user.user.id
        
        # Verify user has access to project through organization
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
        
        # Delete the project
        response = supabase_client.table('projects').delete().eq('id', project_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Project not found")
            
        return JSONResponse({
            "status": "success",
            "message": "Project deleted successfully"
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))