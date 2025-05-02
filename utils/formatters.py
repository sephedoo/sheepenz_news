"""
Text formatting utilities.
"""
import re
import unicodedata
from typing import List, Dict

def sanitize_filename(filename: str) -> str:
    """Create a safe filename from input string"""
    return "".join([c if c.isalnum() else "_" for c in filename])

def slugify(text: str) -> str:
    """
    Convert a string into a URL-friendly slug.
    - Convert to lowercase
    - Replace spaces with hyphens
    - Remove special characters
    - Handle unicode characters
    - Remove leading/trailing hyphens
    """
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = re.sub(r'[\s]+', '-', text)
    # Remove special characters
    text = re.sub(r'[^\w\-]', '', text)
    # Remove duplicate hyphens
    text = re.sub(r'[-]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text

def format_content_as_blocks(text: str) -> List[Dict]:
    """
    Format plain text content into Strapi's Rich Text Blocks format
    
    Args:
        text: Plain text content to format
        
    Returns:
        List of blocks in Strapi's rich text format
    """
    # Split text into paragraphs
    paragraphs = text.split('\n\n')
    blocks = []
    
    for paragraph in paragraphs:
        if paragraph.strip():
            # Create a paragraph block with text children
            blocks.append({
                "type": "paragraph",
                "children": [
                    {
                        "type": "text",
                        "text": paragraph.strip()
                    }
                ]
            })
    
    return blocks