from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.schemas import ProfileScrapeRequest, ProfileScrapeResponse
from services.instagram_scraper import InstagramProfileScraper
from utils.config import username_to_url, url_to_username
import json

router = APIRouter()
scraper = InstagramProfileScraper()

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "message": "Instagram Profile Scraper API is running"}

@router.post("/scrape")
async def scrape_instagram(request: ProfileScrapeRequest):
    """
    Main scrape endpoint - scrape Instagram profiles
    """
    try:
        result = await scraper.scrape_profile(
            usernames=request.usernames,
            results_limit=request.results_limit,
            add_parent_data=request.add_parent_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/username-to-url/{username}")
async def convert_username_to_url(username: str):
    """
    Convert Instagram username to full URL
    """
    try:
        url = username_to_url(username)
        return {
            "username": username,
            "url": url,
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/scrape-profile", response_model=ProfileScrapeResponse)
async def scrape_profile(request: ProfileScrapeRequest):
    """
    Scrape Instagram profile and get latest posts
    """
    try:
        result = await scraper.scrape_profile(
            usernames=request.usernames,
            results_limit=request.results_limit,
            add_parent_data=request.add_parent_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scrape-profile/{username}")
async def scrape_single_profile(
    username: str,
    results_limit: Optional[int] = Query(15, description="Number of posts to retrieve"),
    add_parent_data: Optional[bool] = Query(True, description="Include detailed post data")
):
    """
    Scrape a single Instagram profile
    """
    try:
        result = await scraper.scrape_profile(
            usernames=[username],
            results_limit=results_limit,
            add_parent_data=add_parent_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/{username}")
async def get_profile_info(
    username: str,
    results_limit: Optional[int] = Query(15, description="Number of posts to retrieve"),
    add_parent_data: Optional[bool] = Query(True, description="Include detailed post data")
):
    """
    Get Instagram profile information (same as scrape-profile but different endpoint)
    """
    try:
        result = await scraper.scrape_profile(
            usernames=[username],
            results_limit=results_limit,
            add_parent_data=add_parent_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/{username}/posts")
async def get_profile_posts(
    username: str,
    limit: Optional[int] = Query(10, description="Number of posts to return")
):
    """
    Get only the posts from a profile (simplified response)
    """
    try:
        result = await scraper.get_profile_posts_only(username, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))