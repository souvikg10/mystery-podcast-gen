"""supabase module."""
"""
Supabase client configuration.
"""
from supabase import create_client, Client
from app.config.settings import settings

# Initialize Supabase client
supabase_client: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY
)