"""
Configuration module for loading environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_API_URL = "https://api.openai.com/v1/chat/completions"
DALLE_API_URL = "https://api.openai.com/v1/images/generations"

# Unsplash configuration
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY")
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

# Strapi configuration
STRAPI_URL = os.getenv("STRAPI_URL")
STRAPI_TOKEN = os.getenv("STRAPI_TOKEN")

# Default settings
DEFAULT_MODEL = "gpt-4"
DEFAULT_IMAGE_MODEL = "dall-e-3"
DEFAULT_CATEGORY = "technology"
DEFAULT_COUNT = 5
DEFAULT_IMAGE_FOLDER = "news_images"