import os
from dotenv import load_dotenv

load_dotenv()

def get_apify_token():
    """Get Apify API token from environment variables"""
    # Changed from APIFY_API_TOKEN to API_TOKEN to match your .env file
    token = os.getenv("API_TOKEN", "apify_api_fxEcnGWLG4Ga3eEF0Nfz62tLs8YJU60F2nDB")
    return token

def get_gemini_api_key():
    """Get Gemini API key from environment variables"""
    return os.getenv("GEMINI_API_KEY")

def username_to_url(username: str) -> str:
    """Convert Instagram username to full URL"""
    # Remove @ if present and clean the username
    clean_username = username.replace("@", "").strip()
    return f"https://www.instagram.com/{clean_username}/"

def url_to_username(url: str) -> str:
    """Extract username from Instagram URL"""
    # Handle various URL formats
    if "instagram.com/" in url:
        username = url.split("instagram.com/")[-1].rstrip("/")
        # Remove any additional path segments
        username = username.split("/")[0]
        return username
    return url