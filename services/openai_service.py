"""
Service for interacting with OpenAI APIs.
"""
import json
import datetime
import requests
from typing import List, Dict, Any, Optional

import config
from models.news_item import NewsItem
from utils.formatters import slugify

class OpenAIService:
    """Service class for interacting with OpenAI APIs (ChatGPT and DALL-E)"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the OpenAI service with API key
        
        Args:
            api_key: OpenAI API key (optional, will use environment variable if not provided)
        """
        self.api_key = api_key or config.OPENAI_API_KEY
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Either pass it as an argument or "
                "set the OPENAI_API_KEY environment variable."
            )
        
        self.chat_api_url = config.CHAT_API_URL
        self.dalle_api_url = config.DALLE_API_URL
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_news(self, category: str = "technology", count: int = 1) -> List[Dict[str, Any]]:
        """
        Generate news items using ChatGPT
        
        Args:
            category: News category (e.g., technology, business, politics)
            count: Number of news items to generate
            
        Returns:
            List of dictionaries containing news data
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        prompt = f"""
        Generate {count} latest and important news headlines with summaries about {category} 
        for today ({today}). For each news item, include:
        1. A realistic headline
        3. A plausible source
        4. A category or subtopic
        
        Format the response as a JSON array of objects with the following structure:
        [
            {{
                "title": "Headline",
                "summary": "8 paragraphs",
                "source": "Source Name",
                "published_date": "YYYY-MM-DD",
                "category": "Specific subtopic"
            }}
        ]
        
        Make sure each headline is realistic and could plausibly be a real news story from today.
        """
        
        payload = {
            "model": config.DEFAULT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(self.chat_api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse the JSON response
            news_data = json.loads(content)
            return news_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news from OpenAI: {e}")
            return []
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing OpenAI response: {e}")
            return []
    
    def generate_image(self, prompt: str) -> Optional[str]:
        """
        Generate an image using DALL-E based on a prompt
        
        Args:
            prompt: Text prompt to generate the image
            
        Returns:
            URL of the generated image or None if generation failed
        """
        try:
            payload = {
                "model": config.DEFAULT_IMAGE_MODEL,
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024"
            }
            
            response = requests.post(
                self.dalle_api_url, 
                headers=self.headers, 
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            if "data" in result and len(result["data"]) > 0:
                return result["data"][0]["url"]
                
        except Exception as e:
            print(f"Error generating image with DALL-E: {e}")
        
        return None