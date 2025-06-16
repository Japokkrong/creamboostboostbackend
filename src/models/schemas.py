from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProfileScrapeRequest(BaseModel):
    usernames: List[str] = Field(..., description="List of Instagram usernames to scrape")
    results_limit: Optional[int] = Field(15, description="Number of posts to retrieve per profile")
    add_parent_data: Optional[bool] = Field(True, description="Include detailed post data")

class InstagramPost(BaseModel):
    shortCode: Optional[str] = None
    caption: Optional[str] = None
    likesCount: Optional[int] = None
    commentsCount: Optional[int] = None
    timestamp: Optional[str] = None
    displayUrl: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None

class ProfileData(BaseModel):
    username: Optional[str] = None
    profileUrl: Optional[str] = None  # Added profile URL
    fullName: Optional[str] = None
    biography: Optional[str] = None
    followersCount: Optional[int] = None
    followingCount: Optional[int] = None
    postsCount: Optional[int] = None
    isPrivate: Optional[bool] = None
    isVerified: Optional[bool] = None
    profilePicUrl: Optional[str] = None
    latestPosts: Optional[List[Dict[str, Any]]] = None

class ProfileScrapeResponse(BaseModel):
    success: bool
    profiles_scraped: int
    total_items: int
    data: List[ProfileData]
    message: Optional[str] = None

class PostsOnlyResponse(BaseModel):
    success: bool
    username: str
    profileUrl: Optional[str] = None  # Added profile URL
    posts_count: int
    posts: List[InstagramPost]