"""auth module."""
"""
Models for authentication and user management.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from uuid import UUID

class UserSignIn(BaseModel):
    """User sign-in request data."""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User data returned to the client."""
    id: UUID
    email: EmailStr

class SignInResponse(BaseModel):
    """Response data for successful sign-in."""
    status: str = "success"
    access_token: str
    refresh_token: str
    needs_onboarding: bool
    user: UserResponse

class OnboardingData(BaseModel):
    """User onboarding data."""
    first_name: str
    organization_type: str
    organization_name: Optional[str] = None
    use_case: str

class PasswordReset(BaseModel):
    """Password reset request data."""
    current_password: str
    new_password: str

class OrganizationResponse(BaseModel):
    """Organization data returned to the client."""
    id: UUID
    name: str
    description: Optional[str] = None
    created_at: Any  # Could be datetime but Supabase might return it differently

class UserProjectsResponse(BaseModel):
    """Response data for user projects request."""
    status: str = "success"
    organization: Optional[OrganizationResponse] = None
    projects: list = []

class EmailSignup(BaseModel):
    email: EmailStr
