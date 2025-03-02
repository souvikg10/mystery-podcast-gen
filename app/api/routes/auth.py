"""auth module."""
"""
API routes for authentication and user management.
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

from app.db.supabase import supabase_client
from app.models.auth import UserSignIn, SignInResponse, OnboardingData
from app.api.dependencies import get_current_user
from app.models.auth import PasswordReset

router = APIRouter()

@router.post("/signin", response_model=SignInResponse)
async def sign_in(request: Request):
    """Sign in a user with email and password."""
    try:
        # Get request body
        data = await request.json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")
        
        # Authenticate with Supabase
        auth_response = supabase_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        # Extract the needed information from user and session objects
        user = auth_response.user
        session = auth_response.session
        
        if not user or not session:
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        # Check if user has completed onboarding
        profile_response = supabase_client.table('user_profiles').select('*').eq('user_id', user.id).execute()
        
        needs_onboarding = len(profile_response.data) == 0
        
        # Create a serializable response dict with only the data we need
        response_data = {
            "status": "success",
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "needs_onboarding": needs_onboarding,
            "user": {
                "id": user.id,
                "email": user.email
            }
        }
        
        return response_data
    except Exception as e:
        print(f"Sign-in error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

@router.post("/signout")
async def signout():
    """Sign out the current user."""
    try:
        supabase_client.auth.sign_out()
        return JSONResponse({
            "status": "success",
            "message": "Signed out successfully"
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/user/onboarding")
async def save_onboarding(request: Request):
    """Save user onboarding information."""
    try:
        data = await request.json()
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Extract the token
        token = auth_header.replace("Bearer ", "")
        
        # Get user with the provided token
        user_response = supabase_client.auth.get_user(token)
        user = user_response.user
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        # Create an organization first
        org_name = data.get('organization_name') if data.get('organization_type') == 'company' else f"{data.get('first_name')}'s Organization"
        
        org_response = supabase_client.table('organizations').insert({
            "name": org_name,
            "description": f"Organization for {data.get('first_name')}",
            "created_at": "now()"
        }).execute()
        
        if not org_response.data:
            raise HTTPException(status_code=500, detail="Failed to create organization")
            
        org_id = org_response.data[0]['id']
        
        # Add user as organization admin
        member_response = supabase_client.table('organization_members').insert({
            "organization_id": org_id,
            "user_id": user.id,
            "role": "admin",
            "created_at": "now()"
        }).execute()
        
        # Insert onboarding data with organization_id
        profile_response = supabase_client.table('user_profiles').insert({
            "user_id": user.id,
            "first_name": data.get('first_name'),
            "organization_type": data.get('organization_type'),
            "organization_name": data.get('organization_name'),
            "organization_id": org_id,
            "use_case": data.get('use_case')
        }).execute()
        
        return JSONResponse({
            "status": "success",
            "data": {
                "profile": profile_response.data[0] if profile_response.data else None,
                "organization": org_response.data[0]
            }
        })
    except Exception as e:
        print(f"Error in onboarding: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset-password")
async def reset_password(
    password_data: PasswordReset,
    user: dict = Depends(get_current_user)
):
    """Reset a user's password."""
    try:
        # Verify current password
        try:
            # Use the authenticated user's email with the provided current password
            current_user = user.user
            auth_response = supabase_client.auth.sign_in_with_password({
                "email": current_user.email,
                "password": password_data.current_password
            })
            
            # If we get here, the current password is correct
        except Exception as e:
            # Authentication failed - current password is incorrect
            print(f"Password verification failed: {str(e)}")
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Update the password
        try:
            update_response = supabase_client.auth.admin.update_user_by_id(
                user_id=current_user.id,
                user_attributes={
                    "password": password_data.new_password
                }
            )
            
            # Password updated successfully
            return JSONResponse({
                "status": "success",
                "message": "Password updated successfully"
            })
        except Exception as e:
            print(f"Password update failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update password")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Password reset error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))