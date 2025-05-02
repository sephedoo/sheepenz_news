"""
Image handling utilities.
"""
import os
import requests
from typing import List, Optional
from models.news_item import NewsItem
from utils.formatters import sanitize_filename

def save_images_locally(news_items: List[NewsItem], folder: str = "images") -> None:
    """
    Download and save images locally
    
    Args:
        news_items: List of NewsItem objects with image_url attributes
        folder: Directory to save images in
    """
    os.makedirs(folder, exist_ok=True)
    
    for i, item in enumerate(news_items):
        if not item.image_url:
            continue
            
        try:
            response = requests.get(item.image_url)
            if response.status_code == 200:
                # Create a safe filename from the title
                safe_filename = sanitize_filename(item.title)
                safe_filename = safe_filename[:50]  # Truncate if too long
                
                # Save the image
                img_path = os.path.join(folder, f"{i+1}_{safe_filename}.jpg")
                with open(img_path, "wb") as f:
                    f.write(response.content)
                
                # Store the local image path for Strapi upload
                item.local_image_path = img_path
                
        except Exception as e:
            print(f"Error saving image for '{item.title}': {e}")

def download_image_from_url(image_url: str, output_path: str) -> Optional[str]:
    """
    Download an image from a URL to a local file
    
    Args:
        image_url: URL of the image to download
        output_path: Local path to save the image
        
    Returns:
        Path to the downloaded image or None if download failed
    """
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
        return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None