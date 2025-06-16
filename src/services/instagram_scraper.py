from apify_client import ApifyClient
from typing import List, Dict, Any
from models.schemas import ProfileScrapeResponse, ProfileData, PostsOnlyResponse, InstagramPost
from utils.config import get_apify_token, username_to_url
import json

class InstagramProfileScraper:
    def __init__(self):
        self.client = ApifyClient(get_apify_token())
    
    async def scrape_profile(
        self, 
        usernames: List[str], 
        results_limit: int = 15, 
        add_parent_data: bool = True
    ) -> ProfileScrapeResponse:
        """
        Scrape Instagram profiles using Method 2 (Profile Scraper)
        """
        try:
            print(f"Scraping profiles: {usernames}")
            
            run_input = {
                "usernames": usernames,
                "resultsLimit": results_limit,
                "addParentData": add_parent_data
            }
            
            # Run the Instagram Profile Scraper
            run = self.client.actor("apify/instagram-profile-scraper").call(run_input=run_input)
            
            print(f"Profile scraper completed with status: {run['status']}")
            
            # Get the results
            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
            
            if not items:
                return ProfileScrapeResponse(
                    success=False,
                    profiles_scraped=0,
                    total_items=0,
                    data=[],
                    message="No data found for the specified profiles"
                )
            
            # Process and format the data
            processed_profiles = []
            for item in items:
                username = item.get('username')
                profile_data = ProfileData(
                    username=username,
                    profileUrl=username_to_url(username) if username else None,
                    fullName=item.get('fullName'),
                    biography=item.get('biography'),
                    followersCount=item.get('followersCount'),
                    followingCount=item.get('followingCount'),
                    postsCount=item.get('postsCount'),
                    isPrivate=item.get('isPrivate'),
                    isVerified=item.get('isVerified'),
                    profilePicUrl=item.get('profilePicUrl'),
                    latestPosts=item.get('latestPosts', [])
                )
                processed_profiles.append(profile_data)
            
            return ProfileScrapeResponse(
                success=True,
                profiles_scraped=len(processed_profiles),
                total_items=len(items),
                data=processed_profiles,
                message=f"Successfully scraped {len(processed_profiles)} profiles"
            )
            
        except Exception as e:
            print(f"Error in scrape_profile: {e}")
            return ProfileScrapeResponse(
                success=False,
                profiles_scraped=0,
                total_items=0,
                data=[],
                message=f"Error: {str(e)}"
            )
    
    async def get_profile_posts_only(self, username: str, limit: int = 10) -> PostsOnlyResponse:
        """
        Get only the posts from a profile (simplified response)
        """
        try:
            result = await self.scrape_profile([username], results_limit=limit, add_parent_data=True)
            
            if not result.success or not result.data:
                return PostsOnlyResponse(
                    success=False,
                    username=username,
                    profileUrl=username_to_url(username),
                    posts_count=0,
                    posts=[]
                )
            
            profile = result.data[0]
            posts = []
            
            if profile.latestPosts:
                for post_data in profile.latestPosts[:limit]:
                    post = InstagramPost(
                        shortCode=post_data.get('shortCode'),
                        caption=post_data.get('caption'),
                        likesCount=post_data.get('likesCount'),
                        commentsCount=post_data.get('commentsCount'),
                        timestamp=post_data.get('timestamp'),
                        displayUrl=post_data.get('displayUrl'),
                        type=post_data.get('type'),
                        url=f"https://www.instagram.com/p/{post_data.get('shortCode')}/" if post_data.get('shortCode') else None
                    )
                    posts.append(post)
            
            return PostsOnlyResponse(
                success=True,
                username=username,
                profileUrl=username_to_url(username),
                posts_count=len(posts),
                posts=posts
            )
            
        except Exception as e:
            return PostsOnlyResponse(
                success=False,
                username=username,
                profileUrl=username_to_url(username),
                posts_count=0,
                posts=[]
            )