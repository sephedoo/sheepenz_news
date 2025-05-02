"""
Service for interacting with Strapi CMS API.
"""
import os
import datetime
import requests
from typing import List, Dict, Any, Optional

import config
from models.news_item import NewsItem
from utils.formatters import format_content_as_blocks, slugify
from utils.image_utils import download_image_from_url

class StrapiService:
    """Service class for interacting with Strapi CMS API"""
    
    def __init__(self, api_url: str = None, api_token: str = None):
        """
        Initialize the Strapi service with API URL and token
        
        Args:
            api_url: Strapi API URL (optional, will use environment variable if not provided)
            api_token: Strapi API token (optional, will use environment variable if not provided)
        """
        self.api_url = api_url or config.STRAPI_URL
        self.api_token = api_token or config.STRAPI_TOKEN
        
        if not self.api_url or not self.api_token:
            print("Warning: Strapi URL or token not provided. Upload functionality will be disabled.")
            self.headers = None
        else:
            self.headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
    
    def upload_news_items(self, news_items: List[NewsItem], collection_type: str = "articles") -> List[int]:
        """
        Upload news items to Strapi as articles
        
        Args:
            news_items: List of NewsItem objects to upload
            collection_type: Strapi collection type name (default: 'articles')
            
        Returns:
            List of created article IDs
        """
        if not self.api_url or not self.headers:
            raise ValueError("Strapi URL and token are required for uploading to Strapi")
        
        created_ids = []
        api_endpoint = f"{self.api_url}/api/{collection_type}"
        
        for item in news_items:
            try:
                # Format the date properly
                published_date = item.published_date or datetime.datetime.now().strftime("%Y-%m-%d")
                
                # Format the summary as rich text blocks
                content_blocks = format_content_as_blocks(item.summary)
                
                # Create rich text block component
                rich_text_component = {
                    "__component": "shared.rich-text",
                    "body": f"<p>{item.summary}</p>"
                }
                
                # Step 1: First upload the image if available
                image_id = None
                
                if item.local_image_path:
                    image_id = self.upload_image(item.local_image_path)
                elif item.image_url:
                    # Download the image if we only have a URL
                    print(f"Downloading image from URL: {item.image_url}")
                    try:
                        temp_dir = "temp_images"
                        os.makedirs(temp_dir, exist_ok=True)
                        temp_image_path = os.path.join(temp_dir, f"temp_{slugify(item.title)}.jpg")
                        
                        if download_image_from_url(item.image_url, temp_image_path):
                            image_id = self.upload_image(temp_image_path)
                    except Exception as img_err:
                        print(f"Error downloading/uploading image: {img_err}")
                
                # Step 2: Prepare the article data using the correct Strapi structure with blocks
                article_data = {
                    "data": {
                        "title": item.title,
                        "description": f"News from {item.source}" + (f" - {item.category}" if item.category else ""),
                        "publishedAt": published_date,
                        "slug": item.slug,  # Add the slug to the Strapi data
                        "blocks": [rich_text_component]  # Add rich text component if needed
                    }
                }
                
                # If we have an image, add it to the article data
                if image_id:
                    article_data["data"]["cover"] = image_id
                
                print(f"Uploading article to Strapi: {item.title}")
                print(f"Article slug: {item.slug}")
                print(f"API Endpoint: {api_endpoint}")
                print(f"Image ID: {image_id}")
                
                # Step 3: Create the article with the image already attached
                response = requests.post(
                    api_endpoint,
                    headers=self.headers,
                    json=article_data
                )
                
                # Print response for debugging
                print(f"Response status: {response.status_code}")
                print(f"Response content: {response.text[:200]}...")  # Print first 200 chars of response
                
                response.raise_for_status()
                result = response.json()
                
                # Extract the article ID based on Strapi's response format
                article_id = result.get("data", {}).get("id")
                if not article_id and isinstance(result.get("data"), list) and len(result.get("data", [])) > 0:
                    article_id = result["data"][0]["id"]
                
                if not article_id:
                    print(f"Warning: Could not extract article ID from response: {result}")
                    continue
                
                created_ids.append(article_id)
                print(f"Created article: {item.title} with ID: {article_id}")
                
            except Exception as e:
                print(f"Error uploading article '{item.title}' to Strapi: {e}")
                # Print more detailed error information
                import traceback
                print(traceback.format_exc())
        
        return created_ids
    
    def upload_image(self, image_path: str) -> Optional[int]:
        """
        Upload an image to Strapi
        
        Args:
            image_path: Path to the local image file
            
        Returns:
            The ID of the uploaded image or None if upload failed
        """
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return None
        
        try:
            # Remove Content-Type from headers for file upload
            upload_headers = {k: v for k, v in self.headers.items() 
                            if k != "Content-Type"}
            
            # Upload the file
            upload_url = f"{self.api_url}/api/upload"
            
            with open(image_path, 'rb') as img_file:
                files = {
                    'files': (os.path.basename(image_path), img_file, 'image/jpeg')
                }
                
                response = requests.post(
                    upload_url,
                    headers=upload_headers,
                    files=files
                )
                
                if response.status_code == 201:
                    upload_result = response.json()
                    if upload_result and len(upload_result) > 0:
                        media_id = upload_result[0]['id']
                        print(f"Image uploaded successfully. Media ID: {media_id}")
                        return media_id
                else:
                    print(f"Failed to upload image. Status: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"Error uploading image to Strapi: {e}")
            return None