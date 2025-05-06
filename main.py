#!/usr/bin/env python3
"""
Main entry point for the news generator application.
"""
import os
import argparse
import traceback

import config
from models.news_item import NewsItem
from services.openai_service import OpenAIService
from services.unsplash_service import UnsplashService
from services.strapi_service import StrapiService
from services.news_manager import NewsManager

def main():
    """Main function to parse arguments and run the news generator"""
    parser = argparse.ArgumentParser(description="Fetch latest news using ChatGPT and upload to Strapi")
    parser.add_argument("-k", "--api-key", help="OpenAI API key")
    parser.add_argument("--unsplash-key", help="Unsplash API key")
    parser.add_argument("-c", "--category", default=config.DEFAULT_CATEGORY, 
                        help="News category (technology, business, etc.)")
    parser.add_argument("-n", "--count", type=int, default=config.DEFAULT_COUNT,
                        help="Number of news items to fetch")
    parser.add_argument("-o", "--output", help="Output JSON file name")
    parser.add_argument("-s", "--save", action="store_true", 
                        help="Save results to JSON file")
    parser.add_argument("--html", action="store_true",
                        help="Generate HTML report")
    parser.add_argument("--download-images", action="store_true",
                        help="Download images locally")
    parser.add_argument("--image-folder", default=config.DEFAULT_IMAGE_FOLDER,
                        help="Folder to save downloaded images")
    parser.add_argument("--strapi-url", default=config.STRAPI_URL,
                        help="Strapi API URL")
    parser.add_argument("--strapi-token", default= config.STRAPI_TOKEN ,help="Strapi API token")
    parser.add_argument("--strapi-collection", default="articles",
                        help="Strapi collection type name")
    parser.add_argument("--upload-to-strapi",default=True, action="store_true",
                        help="Upload news items to Strapi")
    parser.add_argument("--force-fetch", action="store_true",
                        help="Force fetching new news even if today's news exists")
    
    args = parser.parse_args()
    
    try:
        # Initialize services
        openai_service = OpenAIService(api_key=args.api_key)
        unsplash_service = UnsplashService(api_key=args.unsplash_key)
        strapi_service = StrapiService(api_url=args.strapi_url, api_token=args.strapi_token)
        
        # Create news manager
        news_manager = NewsManager(
            openai_service=openai_service,
            unsplash_service=unsplash_service,
            strapi_service=strapi_service
        )
        
        # Process news
        news_items = news_manager.process_news(
            category=args.category,
            count=args.count,
            force_fetch=args.force_fetch,
            save_json=args.save,
            download_images=args.download_images or args.upload_to_strapi,
            upload_to_strapi=args.upload_to_strapi,
            image_folder=args.image_folder
        )
        
        # If specific output file specified, save to that file
        if args.output and args.save:
            news_manager.save_news_to_json(news_items, args.output)
            
        # Generate HTML report if requested
        if args.html:
            generate_html_report(news_items, f"{args.category}_news_report.html")
            
        print(f"Successfully processed {len(news_items)} news items.")
            
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

def generate_html_report(news_items, output_file):
    """Generate a simple HTML report for the news items"""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>News Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .news-item { margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
        .news-title { font-size: 24px; margin-bottom: 10px; }
        .news-meta { color: #666; margin-bottom: 10px; }
        .news-summary { line-height: 1.5; }
        img { max-width: 100%; height: auto; margin-bottom: 15px; }
    </style>
</head>
<body>
    <h1>Generated News Report</h1>
"""
    
    for item in news_items:
        html += f"""
    <div class="news-item">
        <h2 class="news-title">{item.title}</h2>
        <div class="news-meta">
            Source: {item.source}
            {f" | Category: {item.category}" if item.category else ""}
            {f" | Published: {item.published_date}" if item.published_date else ""}
        </div>
"""
        
        if item.image_url:
            html += f'        <img src="{item.image_url}" alt="{item.title}">\n'
        elif item.local_image_path:
            html += f'        <img src="{os.path.relpath(item.local_image_path)}" alt="{item.title}">\n'
            
        html += f"""
        <div class="news-summary">
            {item.summary.replace("\n", "<br>")}
        </div>
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"HTML report generated: {output_file}")

if __name__ == "__main__":
    main()