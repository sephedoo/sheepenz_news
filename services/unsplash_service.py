"""
Service for interacting with Unsplash API.
"""
import requests
from typing import Optional

import config

class UnsplashService:
    """Service class for interacting with Unsplash API"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Unsplash service with API key
        
        Args:
            api_key: Unsplash API key (optional, will use environment variable if not provided)
        """
        self.api_key = api_key or config.UNSPLASH_API_KEY
        
        if not self.api_key:
            print("Warning: Unsplash API key not provided. Image search functionality will be limited.")
            self.headers = None
        else:
            self.headers = {
                "Authorization": f"Client-ID {self.api_key}"
            }
        
        self.api_url = config.UNSPLASH_API_URL
    
    def search_image(self, query: str, orientation: str = "landscape") -> Optional[str]:
        """
        Search for an image on Unsplash
        
        Args:
            query: Search term
            orientation: Image orientation (landscape, portrait, or squarish)
            
        Returns:
            URL of an image or None if no image found or API key not provided
        """
        if not self.headers:
            return None
            
        try:
            params = {
                "query": query,
                "per_page": 1,
                "orientation": orientation
            }
            
            response = requests.get(
                self.api_url, 
                headers=self.headers, 
                params=params
            )
            response.raise_for_status()
            result = response.json()
            
            if result["results"] and len(result["results"]) > 0:
                return result["results"][0]["urls"]["regular"]
                
        except Exception as e:
            print(f"Error searching for image on Unsplash: {e}")
        
        return None