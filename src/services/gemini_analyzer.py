import google.generativeai as genai
import json
from typing import Dict, Any, List
from utils.config import get_gemini_api_key
from datetime import datetime
import re

class GeminiProfileAnalyzer:
    def __init__(self):
        api_key = get_gemini_api_key()
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def analyze_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Instagram profile using Gemini AI with enhanced prompts
        """
        try:
            prompt = self._create_enhanced_analysis_prompt(profile_data)
            
            response = self.model.generate_content(prompt)
            analysis_text = response.text
            
            # Clean up the response
            analysis_text = self._clean_json_response(analysis_text)
            
            try:
                analysis_result = json.loads(analysis_text)
                # Validate and enhance the result
                return self._validate_and_enhance_result(analysis_result, profile_data)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")
                print(f"Response text: {analysis_text}")
                return self._get_enhanced_fallback_analysis(profile_data)
            
        except Exception as e:
            print(f"Error in Gemini analysis: {e}")
            return self._get_enhanced_fallback_analysis(profile_data)
    
    def _create_enhanced_analysis_prompt(self, profile_data: Dict[str, Any]) -> str:
        """Create enhanced analysis prompt tailored for dating/social app context"""
        
        # Extract and analyze content
        posts = profile_data.get('posts', [])
        post_captions = []
        hashtags = []
        total_engagement = 0
        
        for post in posts[:10]:
            caption = post.get('caption', '')
            if caption:
                post_captions.append(caption)
                # Extract hashtags
                hashtags.extend(re.findall(r'#\w+', caption.lower()))
                # Calculate engagement
                likes = post.get('likes', 0)
                comments = post.get('comments', 0)
                total_engagement += likes + comments
        
        posts_text = '\n---\n'.join(post_captions) if post_captions else 'No recent posts available'
        unique_hashtags = list(set(hashtags))[:10]  # Top 10 unique hashtags
        
        bio = profile_data.get('bio', '')
        follower_count = profile_data.get('follower_count', 0)
        following_count = profile_data.get('following_count', 0)
        post_count = profile_data.get('post_count', 0)
        
        # Calculate engagement rate
        avg_engagement = total_engagement / len(posts) if posts else 0
        engagement_rate = (avg_engagement / follower_count * 100) if follower_count > 0 else 0
        
        prompt = f"""
You are an expert social media analyst specializing in personality insights for dating and social networking apps. Analyze this Instagram profile and provide detailed insights that would help someone understand this person's personality, interests, and how to connect with them.

PROFILE DATA:
Name: {profile_data.get('display_name', 'N/A')}
Username: @{profile_data.get('username', 'N/A')}
Bio: "{bio}"
Followers: {follower_count:,}
Following: {following_count:,}
Posts: {post_count}
Engagement Rate: {engagement_rate:.1f}%

RECENT POST CONTENT:
{posts_text}

HASHTAGS USED: {', '.join(unique_hashtags) if unique_hashtags else 'None detected'}

ANALYSIS INSTRUCTIONS:
1. Focus on personality traits that would be relevant for dating/friendship connections
2. Identify genuine interests (not just surface-level hobbies)
3. Create conversation starters that feel natural and engaging
4. Analyze communication style for compatibility insights
5. Provide realistic confidence scores based on evidence

Return ONLY a valid JSON object with this EXACT structure:

{{
  "personality_traits": [
    {{
      "trait": "Creative",
      "confidence": 0.85,
      "description": "Demonstrates artistic expression and creative thinking through visual content and captions",
      "evidence": "Multiple artistic posts with thoughtful composition and creative captions"
    }},
    {{
      "trait": "Adventurous", 
      "confidence": 0.72,
      "description": "Shows willingness to try new experiences and explore different places",
      "evidence": "Travel posts and trying new activities"
    }},
    {{
      "trait": "Social",
      "confidence": 0.68,
      "description": "Enjoys connecting with others and sharing experiences",
      "evidence": "Group photos and social event posts"
    }}
  ],
  "interests": [
    {{
      "name": "Photography",
      "confidence": 0.90,
      "category": "art"
    }},
    {{
      "name": "Travel",
      "confidence": 0.85,
      "category": "travel"
    }},
    {{
      "name": "Fitness",
      "confidence": 0.75,
      "category": "wellness"
    }},
    {{
      "name": "Food & Cooking",
      "confidence": 0.70,
      "category": "food"
    }}
  ],
  "conversation_starters": [
    "I noticed you have a great eye for photography - what got you into capturing those kinds of moments?",
    "Your travel photos are incredible! What's been your favorite destination so far?",
    "I love your creative content - do you have any tips for someone just getting into [specific interest]?"
  ],
  "communication_style": {{
    "tone": "warm",
    "formality_level": "casual",
    "emoji_usage": "moderate",
    "posting_frequency": "regular", 
    "engagement_style": "interactive",
    "language_complexity": "moderate"
  }},
  "content_analysis": {{
    "top_hashtags": {json.dumps(unique_hashtags[:5])},
    "posting_patterns": {{
      "most_active_time": "evening",
      "most_active_day": "weekend",
      "average_posts_per_week": {max(1, post_count // 52) if post_count > 52 else post_count}
    }},
    "content_themes": ["photography", "lifestyle", "travel", "food"],
    "engagement_metrics": {{
      "average_likes": {int(avg_engagement * 0.8) if avg_engagement > 0 else 50},
      "average_comments": {int(avg_engagement * 0.2) if avg_engagement > 0 else 10},
      "engagement_rate": {engagement_rate:.1f}
    }}
  }},
  "social_signals": {{
    "lifestyle_indicators": ["urban_professional", "creative_type", "social_butterfly"],
    "values": ["authenticity", "creativity", "adventure"],
    "relationship_readiness": "open_to_connections",
    "communication_preference": "visual_storytelling"
  }},
  "metadata": {{
    "analyzed_at": "{datetime.now().isoformat()}",
    "confidence_score": 0.82,
    "data_points_analyzed": {len(post_captions) + (1 if bio else 0) + len(unique_hashtags)}
  }}
}}

IMPORTANT GUIDELINES:
- Base ALL insights on actual profile data provided
- Use confidence scores between 0.6-0.95 (be realistic)
- Focus on positive traits and genuine interests
- Make conversation starters specific and personalized
- Ensure all JSON is valid and properly formatted
- Categories for interests: art, travel, fitness, food, music, technology, wellness, sports, business, fashion
"""
        return prompt
    
    def _clean_json_response(self, text: str) -> str:
        """Clean up JSON response from Gemini"""
        # Remove markdown formatting
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        # Remove any leading/trailing whitespace and newlines
        text = text.strip()
        
        # Fix common JSON formatting issues
        text = text.replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _validate_and_enhance_result(self, result: Dict[str, Any], profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance the analysis result"""
        
        # Ensure required fields exist
        if 'personality_traits' not in result:
            result['personality_traits'] = []
        if 'interests' not in result:
            result['interests'] = []
        if 'conversation_starters' not in result:
            result['conversation_starters'] = []
            
        # Ensure minimum number of items
        if len(result['personality_traits']) < 2:
            result['personality_traits'].extend(self._get_default_traits()[:3-len(result['personality_traits'])])
        
        if len(result['interests']) < 2:
            result['interests'].extend(self._get_default_interests()[:4-len(result['interests'])])
            
        if len(result['conversation_starters']) < 2:
            result['conversation_starters'].extend(self._get_default_conversation_starters()[:3-len(result['conversation_starters'])])
        
        # Add missing sections if not present
        if 'social_signals' not in result:
            result['social_signals'] = {
                "lifestyle_indicators": ["social_media_savvy"],
                "values": ["authenticity"],
                "relationship_readiness": "open_to_connections", 
                "communication_preference": "digital_native"
            }
        
        return result
    
    def _get_default_traits(self) -> List[Dict[str, Any]]:
        """Default personality traits"""
        return [
            {
                "trait": "Authentic",
                "confidence": 0.70,
                "description": "Shows genuine personality through posts",
                "evidence": "Natural and unfiltered content style"
            },
            {
                "trait": "Social",
                "confidence": 0.65,
                "description": "Enjoys sharing experiences with others",
                "evidence": "Active social media presence"
            },
            {
                "trait": "Creative",
                "confidence": 0.60,
                "description": "Expresses creativity through content choices",
                "evidence": "Thoughtful post composition"
            }
        ]
    
    def _get_default_interests(self) -> List[Dict[str, Any]]:
        """Default interests"""
        return [
            {"name": "Social Media", "confidence": 0.80, "category": "technology"},
            {"name": "Photography", "confidence": 0.70, "category": "art"},
            {"name": "Lifestyle", "confidence": 0.65, "category": "wellness"},
            {"name": "Communication", "confidence": 0.60, "category": "social"}
        ]
    
    def _get_default_conversation_starters(self) -> List[str]:
        """Default conversation starters"""
        return [
            "I'd love to learn more about your interests - what are you most passionate about?",
            "Your profile shows great personality! What's something fun you've been up to lately?",
            "I noticed we might have some interests in common - what do you enjoy doing in your free time?"
        ]
    
    def _get_enhanced_fallback_analysis(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced fallback analysis with real data"""
        follower_count = profile_data.get('follower_count', 0)
        bio = profile_data.get('bio', '')
        posts = profile_data.get('posts', [])
        
        # Analyze bio for interests
        bio_lower = bio.lower()
        detected_interests = []
        
        interest_keywords = {
            "photography": ["photo", "camera", "shot", "capture", "lens"],
            "travel": ["travel", "explore", "adventure", "journey", "wanderlust"],
            "fitness": ["fitness", "gym", "workout", "health", "running"],
            "food": ["food", "cook", "chef", "recipe", "foodie"],
            "art": ["art", "creative", "design", "artist", "paint"],
            "music": ["music", "song", "concert", "band", "guitar"]
        }
        
        for category, keywords in interest_keywords.items():
            if any(keyword in bio_lower for keyword in keywords):
                detected_interests.append({
                    "name": category.title(),
                    "confidence": 0.75,
                    "category": category
                })
        
        # Default interests if none detected
        if not detected_interests:
            detected_interests = self._get_default_interests()
        
        return {
            "personality_traits": self._get_default_traits(),
            "interests": detected_interests[:4],
            "conversation_starters": [
                f"I noticed from your bio that you're into {detected_interests[0]['name'].lower()} - what got you started with that?",
                "Your profile caught my attention! What's something you're really passionate about?",
                "I'd love to learn more about what makes you tick - what do you enjoy doing most?"
            ],
            "communication_style": {
                "tone": "friendly",
                "formality_level": "casual", 
                "emoji_usage": "moderate",
                "posting_frequency": "regular",
                "engagement_style": "moderate",
                "language_complexity": "moderate"
            },
            "content_analysis": {
                "top_hashtags": ["#lifestyle", "#instagram"],
                "posting_patterns": {
                    "most_active_time": "evening",
                    "most_active_day": "weekend",
                    "average_posts_per_week": max(1, len(posts) // 4) if posts else 3
                },
                "content_themes": ["lifestyle", "social"],
                "engagement_metrics": {
                    "average_likes": max(10, follower_count * 0.03),
                    "average_comments": max(2, follower_count * 0.005),
                    "engagement_rate": 3.5
                }
            },
            "social_signals": {
                "lifestyle_indicators": ["social_media_active", "digitally_connected"],
                "values": ["authenticity", "connection"],
                "relationship_readiness": "open_to_connections",
                "communication_preference": "visual_and_text"
            },
            "metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "confidence_score": 0.65,
                "data_points_analyzed": len(posts) + (1 if bio else 0)
            }
        }