"""
News manager service for coordinating all news-related operations.
"""
import os
import json
import datetime
import fnmatch
from typing import List, Dict, Any, Optional

from models.news_item import NewsItem
from services.openai_service import OpenAIService
from services.unsplash_service import UnsplashService
from services.strapi_service import StrapiService
from utils.formatters import sanitize_filename, slugify
from utils.image_utils import save_images_locally

class NewsManager:
    """Manager class to coordinate news generation, image fetching, and publishing"""
    
    def __init__(self, openai_service: OpenAIService, unsplash_service: UnsplashService, 
                 strapi_service: StrapiService):
        """
        Initialize the news manager with required services
        
        Args:
            openai_service: Service for OpenAI API
            unsplash_service: Service for Unsplash API
            strapi_service: Service for Strapi CMS API
        """
        self.openai_service = openai_service
        self.unsplash_service = unsplash_service
        self.strapi_service = strapi_service
    
    def generate_news_items(self, category: str = "technology", count: int = 1) -> List[NewsItem]:
        """
        Generate news items with associated images
        
        Args:
            category: News category (e.g., technology, business, politics)
            count: Number of news items to generate
            
        Returns:
            List of NewsItem objects
        """
        # Generate news data using OpenAI
        news_data = self.openai_service.generate_news(category=category, count=count)
        
        news_items = []
        for item in news_data:
            news_item = NewsItem(
                title=item["title"],
                summary=item["summary"],
                source=item["source"],
                published_date=item.get("published_date"),
                category=item.get("category")
            )
            
            # Generate a slug from the title
            news_item.slug = slugify(news_item.title)
            
            # Get an image for this news item
            image_query = f"{news_item.title} {news_item.category if news_item.category else category}"
            
            # Try Unsplash first
            image_url = self.unsplash_service.search_image(image_query)
            
            # Fall back to DALL-E if Unsplash fails
            if not image_url:
                prompt = f"Generate a realistic news image for headline: '{news_item.title}'"
                if news_item.category:
                    prompt += f" in the category of {news_item.category}"
                
                image_url = self.openai_service.generate_image(prompt)
            
            if image_url:
                news_item.image_url = image_url
            
            news_items.append(news_item)
        
        return news_items
    
    def save_news_to_json(self, news_items: List[NewsItem], filename: str) -> None:
        """
        Save news items to a JSON file
        
        Args:
            news_items: List of NewsItem objects to save
            filename: Path to save the JSON file
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([item.to_dict() for item in news_items], f, indent=2, ensure_ascii=False)
        print(f"News saved to {filename}")
    
    def load_news_from_json(self, filename: str) -> List[NewsItem]:
        """
        Load news items from a JSON file
        
        Args:
            filename: Path to the JSON file
            
        Returns:
            List of NewsItem objects
        """
        if not os.path.exists(filename):
            return []
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            
            news_items = []
            for item_data in news_data:
                news_item = NewsItem(
                    title=item_data["title"],
                    summary=item_data["summary"],
                    source=item_data["source"],
                    url=item_data.get("url"),
                    published_date=item_data.get("published_date"),
                    category=item_data.get("category"),
                    image_url=item_data.get("image_url"),
                    slug=item_data.get("slug")
                )
                
                # Generate slug if not present
                if not news_item.slug:
                    news_item.slug = slugify(news_item.title)
                
                news_items.append(news_item)
            
            return news_items
            
        except Exception as e:
            print(f"Error loading news from {filename}: {e}")
            return []
    
    def find_local_images(self, news_items: List[NewsItem], image_folder: str) -> None:
        """
        Find local images for news items based on their titles
        
        Args:
            news_items: List of NewsItem objects
            image_folder: Folder containing images
        """
        if not os.path.exists(image_folder):
            return
            
        for item in news_items:
            # Check if there's a corresponding local image
            image_filename_pattern = f"*_{sanitize_filename(item.title)[:50]}.jpg"
            
            for file in os.listdir(image_folder):
                if fnmatch.fnmatch(file, image_filename_pattern):
                    item.local_image_path = os.path.join(image_folder, file)
                    break
    
    def process_news(self, category: str, count: int, force_fetch: bool = False, 
                    save_json: bool = True, download_images: bool = True, 
                    upload_to_strapi: bool = False, image_folder: str = "news_images") -> List[NewsItem]:
        """
        Complete news processing pipeline: generate/load news, save to JSON, download images, upload to Strapi
        
        Args:
            category: News category
            count: Number of news items
            force_fetch: Whether to force fetching new news even if cached news exists
            save_json: Whether to save news to JSON
            download_images: Whether to download images
            upload_to_strapi: Whether to upload to Strapi
            image_folder: Folder to save downloaded images
            
        Returns:
            List of processed NewsItem objects
        """
        # Check if today's news already exists in JSON file
        today_date = datetime.datetime.now().strftime("%Y%m%d")
        default_json_file = f"{category}_news_{today_date}.json"
        
        news_items = []
        
        # Check if we should use cached news
        if not force_fetch and os.path.exists(default_json_file):
            print(f"Found today's news file: {default_json_file}")
            news_items = self.load_news_from_json(default_json_file)
            
            if news_items:
                print(f"Loaded {len(news_items)} news items from cache.")
                # Find local images for cached news items
                self.find_local_images(news_items, image_folder)
        
        # If no cached news or force fetch is enabled, fetch fresh news
        if not news_items or force_fetch:
            print("Generating fresh news...")
            news_items = self.generate_news_items(category=category, count=count)
            
            # Save to JSON if requested
            if save_json:
                self.save_news_to_json(news_items, default_json_file)
        
        # Download images if requested
        if download_images:
            save_images_locally(news_items, folder=image_folder)
            
        # Upload to Strapi if requested
        if upload_to_strapi:
            self.strapi_service.upload_news_items(news_items)
            
        return news_items