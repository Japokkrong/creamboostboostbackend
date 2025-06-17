from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import List, Optional
import httpx
from models.schemas import ProfileScrapeRequest, ProfileScrapeResponse
from services.instagram_scraper import InstagramProfileScraper
from services.gemini_analyzer import GeminiProfileAnalyzer
from utils.config import username_to_url, url_to_username
import json
import traceback
from datetime import datetime

router = APIRouter()
scraper = InstagramProfileScraper()
gemini_analyzer = GeminiProfileAnalyzer()

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "message": "Instagram Profile Scraper API is running"}

@router.get("/proxy-image")
async def proxy_image(url: str):
    """
    Proxy endpoint to fetch images and avoid CORS issues
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch image")
            
            content_type = response.headers.get("content-type", "image/jpeg")
            
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=3600",
                    "Access-Control-Allow-Origin": "*"
                }
            )
            
    except Exception as e:
        print(f"Error proxying image: {e}")
        raise HTTPException(status_code=500, detail="Failed to load image")

@router.post("/scrape-profile")
async def scrape_profile_frontend(request: dict):
    """
    Scrape profile endpoint for frontend - returns frontend-compatible format
    """
    try:
        print(f"=== FRONTEND REQUEST DEBUG ===")
        print(f"Full request: {request}")
        
        # Extract username from URL
        profile_url = request.get('profileUrl', '')
        print(f"Profile URL from request: {profile_url}")
        
        if not profile_url:
            return {
                "metadata": {
                    "success": False,
                    "error_message": "No profileUrl provided in request"
                }
            }
        
        username = url_to_username(profile_url)
        print(f"Extracted username: {username}")
        
        if not username:
            return {
                "metadata": {
                    "success": False,
                    "error_message": f"Could not extract username from URL: {profile_url}"
                }
            }
        
        # Use the existing scraper
        result = await scraper.scrape_profile(
            usernames=[username],
            results_limit=15,
            add_parent_data=True
        )
        
        print(f"Scraper result: {result}")
        
        if not result.success or not result.data:
            return {
                "metadata": {
                    "success": False,
                    "error_message": result.message or "Failed to scrape profile"
                }
            }
        
        profile_data = result.data[0]
        
        # Convert to frontend format
        frontend_response = {
            "display_name": profile_data.fullName or username,
            "username": username,
            "platform": "instagram",
            "bio": profile_data.biography or "",
            "follower_count": profile_data.followersCount or 0,
            "following_count": profile_data.followingCount or 0,
            "post_count": profile_data.postsCount or 0,
            "profile_image_url": profile_data.profilePicUrl or "",
            "is_verified": profile_data.isVerified or False,
            "url": profile_data.profileUrl or username_to_url(username),
            "posts": [],
            "metadata": {
                "success": True,
                "scraped_at": datetime.now().isoformat(),
                "platform": "instagram"
            }
        }
        
        # Add posts if available
        if profile_data.latestPosts:
            for post in profile_data.latestPosts[:10]:
                frontend_response["posts"].append({
                    "id": post.get("shortCode", ""),
                    "caption": post.get("caption", ""),
                    "likes": post.get("likesCount", 0),
                    "comments": post.get("commentsCount", 0),
                    "timestamp": post.get("timestamp", ""),
                    "image_url": post.get("displayUrl", ""),
                    "url": f"https://www.instagram.com/p/{post.get('shortCode')}/" if post.get('shortCode') else ""
                })
        
        return frontend_response
        
    except Exception as e:
        print(f"Error in scrape_profile_frontend: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "metadata": {
                "success": False,
                "error_message": str(e)
            }
        }

@router.post("/analyze-profile")
async def analyze_profile_with_gemini(request: dict):
    """
    Analyze profile using Gemini AI
    """
    try:
        print(f"=== GEMINI ANALYSIS REQUEST ===")
        print(f"Request: {request}")
        
        profile_url = request.get('profileUrl', '')
        
        if not profile_url:
            raise HTTPException(status_code=400, detail="profileUrl is required")
        
        # First scrape the profile
        username = url_to_username(profile_url)
        scrape_result = await scraper.scrape_profile(
            usernames=[username],
            results_limit=15,
            add_parent_data=True
        )
        
        if not scrape_result.success or not scrape_result.data:
            raise HTTPException(status_code=400, detail="Failed to scrape profile for analysis")
        
        profile_data = scrape_result.data[0]
        
        # Prepare data for Gemini analysis
        analysis_data = {
            "display_name": profile_data.fullName or username,
            "username": username,
            "bio": profile_data.biography or "",
            "follower_count": profile_data.followersCount or 0,
            "following_count": profile_data.followingCount or 0,
            "post_count": profile_data.postsCount or 0,
            "posts": []
        }
        
        # Add post data
        if profile_data.latestPosts:
            for post in profile_data.latestPosts[:10]:
                analysis_data["posts"].append({
                    "caption": post.get("caption", ""),
                    "likes": post.get("likesCount", 0),
                    "comments": post.get("commentsCount", 0)
                })
        
        # Analyze with Gemini
        analysis_result = await gemini_analyzer.analyze_profile(analysis_data)
        
        print(f"=== GEMINI ANALYSIS RESULT ===")
        print(f"Result: {analysis_result}")
        
        return analysis_result
        
    except Exception as e:
        print(f"Error in analyze_profile_with_gemini: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

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
    Get Instagram profile information
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
    Get only the posts from a profile
    """
    try:
        result = await scraper.get_profile_posts_only(username, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Add these new endpoints after your existing ones

@router.post("/conversation-starters")
async def generate_conversation_starters(request: dict):
    """
    Generate conversation starters using Gemini AI
    """
    try:
        print(f"=== CONVERSATION STARTERS REQUEST ===")
        print(f"Request: {request}")
        
        profile_analysis = request.get('profile_analysis', {})
        language = request.get('language', 'en')
        category = request.get('category')
        tone = request.get('tone', 'casual')
        count = request.get('count', 8)
        
        # Create prompt for conversation starters
        interests = profile_analysis.get('interests', [])[:3]
        personality_traits = profile_analysis.get('personality_traits', [])[:2]
        communication_style = profile_analysis.get('communication_style', 'casual')
        
        prompt = f"""
Generate {count} conversation starters in {language} language for someone with these characteristics:

Interests: {', '.join(interests)}
Personality Traits: {', '.join(personality_traits)}
Communication Style: {communication_style}
Preferred Category: {category or 'general'}
Preferred Tone: {tone}

Generate conversation starters that are:
1. Natural and engaging
2. Based on the person's interests
3. Appropriate for {language} culture
4. In {tone} tone

Return ONLY a JSON array with this format:
[
  {{
    "id": "starter-1",
    "category": "{category or 'general'}",
    "tone": "{tone}",
    "text": "Your conversation starter text here",
    "context": "Context about when to use this starter",
    "cultural_notes": "Any cultural considerations"
  }}
]
"""
        
        # Use Gemini to generate starters
        response = await gemini_analyzer.model.generate_content(prompt)
        
        # Clean and parse response
        text = response.text.strip()
        if text.startswith('```json'):
            text = text.replace('```json', '').replace('```', '')
        
        try:
            starters = json.loads(text)
            return {"conversation_starters": starters}
        except json.JSONDecodeError:
            # Return fallback starters
            return {"conversation_starters": get_fallback_starters(language, category, tone, count)}
        
    except Exception as e:
        print(f"Error generating conversation starters: {e}")
        return {"conversation_starters": get_fallback_starters(language, category, tone, count)}

@router.post("/response-suggestions")
async def generate_response_suggestions(request: dict):
    """
    Generate response suggestions using Gemini AI
    """
    try:
        print(f"=== RESPONSE SUGGESTIONS REQUEST ===")
        print(f"Request: {request}")
        
        message = request.get('message', '')
        context = request.get('context', '')
        language = request.get('language', 'en')
        styles = request.get('styles', ['engaging', 'playful', 'supportive', 'professional'])
        
        prompt = f"""
Generate response suggestions in {language} language for this message: "{message}"

Context: {context}

Generate {len(styles)} different response styles: {', '.join(styles)}

Each response should be:
1. Natural and contextually appropriate
2. Match the specified style
3. Be culturally appropriate for {language}
4. Include reasoning for why this response works

Return ONLY a JSON array with this format:
[
  {{
    "type": "engaging",
    "text": "Your response text here",
    "reasoning": "Why this response works well"
  }}
]
"""
        
        # Use Gemini to generate responses
        response = await gemini_analyzer.model.generate_content(prompt)
        
        # Clean and parse response
        text = response.text.strip()
        if text.startswith('```json'):
            text = text.replace('```json', '').replace('```', '')
        
        try:
            suggestions = json.loads(text)
            return {"suggestions": suggestions}
        except json.JSONDecodeError:
            # Return fallback suggestions
            return {"suggestions": get_fallback_responses(language, message)}
        
    except Exception as e:
        print(f"Error generating response suggestions: {e}")
        return {"suggestions": get_fallback_responses(language, message)}

# Helper functions for fallback responses
def get_fallback_starters(language: str, category: str, tone: str, count: int):
    """Fallback conversation starters"""
    if language == 'th':
        starters = [
            {
                "id": "starter-1",
                "category": category or "general",
                "tone": tone,
                "text": "สวัสดีครับ/ค่ะ เห็นว่าคุณสนใจเรื่องนี้ด้วยนะ อยากฟังความคิดเห็นของคุณเกี่ยวกับเรื่องนี้",
                "context": "เริ่มต้นการสนทนาทั่วไป",
                "cultural_notes": "การทักทายแบบสุภาพในวัฒนธรรมไทย"
            },
            {
                "id": "starter-2", 
                "category": category or "general",
                "tone": tone,
                "text": "เห็นโปรไฟล์แล้วดูน่าสนใจมากเลย มีอะไรแนะนำไหมคะ?",
                "context": "แสดงความสนใจในโปรไฟล์",
                "cultural_notes": "การแสดงความสนใจอย่างสุภาพ"
            }
        ]
    else:
        starters = [
            {
                "id": "starter-1",
                "category": category or "general", 
                "tone": tone,
                "text": "I noticed we have some similar interests! What got you into that?",
                "context": "Opening based on shared interests",
                "cultural_notes": "Shows genuine interest in learning about them"
            },
            {
                "id": "starter-2",
                "category": category or "general",
                "tone": tone, 
                "text": "Your profile caught my attention! What's something you're really passionate about lately?",
                "context": "General opener showing interest",
                "cultural_notes": "Casual and engaging tone"
            }
        ]
    
    return starters[:count]

def get_fallback_responses(language: str, message: str):
    """Fallback response suggestions"""
    if language == 'th':
        return [
            {
                "type": "engaging",
                "text": "น่าสนใจมากเลย! อยากรู้รายละเอียดเพิ่มเติม",
                "reasoning": "แสดงความสนใจและขอข้อมูลเพิ่ม"
            },
            {
                "type": "supportive", 
                "text": "เก่งมากเลยครับ/ค่ะ! ให้กำลังใจ",
                "reasoning": "ให้การสนับสนุนและกำลังใจ"
            }
        ]
    else:
        return [
            {
                "type": "engaging",
                "text": "That's really interesting! I'd love to hear more about that.",
                "reasoning": "Shows genuine interest and encourages them to share more"
            },
            {
                "type": "supportive",
                "text": "That sounds amazing! You should be proud of that accomplishment.",
                "reasoning": "Provides positive reinforcement and acknowledgment"
            }
        ]