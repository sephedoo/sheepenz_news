# News Generator

An AI-powered automated news generation and publishing system that generates realistic news articles using OpenAI's GPT-4, finds or creates relevant images, and publishes them to a Strapi CMS.

## Features

- Generate realistic news articles with titles, summaries, and sources using OpenAI's GPT-4
- Fetch relevant images from Unsplash or generate them with DALL-E
- Save news to JSON files for caching
- Upload news articles to Strapi CMS
- Generate HTML reports

## Project Structure

```
news_generator/
├── .env                    # Environment variables
├── requirements.txt        # Dependencies 
├── main.py                 # Entry point
├── models/
│   └── news_item.py        # NewsItem data class
├── utils/
│   ├── __init__.py
│   ├── formatters.py       # Text formatting utilities
│   └── image_utils.py      # Image handling utilities
├── services/
│   ├── __init__.py
│   ├── openai_service.py   # OpenAI API service
│   ├── unsplash_service.py # Unsplash API service
│   └── strapi_service.py   # Strapi API service
└── config.py               # Configuration from environment variables
```

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   UNSPLASH_API_KEY=your_unsplash_api_key
   STRAPI_URL=your_strapi_url
   STRAPI_TOKEN=your_strapi_token
   ```

## Usage

Basic usage:
```
python main.py --category technology --count 5 --save --download-images
```

Upload to Strapi:
```
python main.py --category technology --count 5 --upload-to-strapi
```

Force fresh news generation:
```
python main.py --category business --count 3 --force-fetch --save
```

Generate HTML report:
```
python main.py --category politics --count 5 --save --html
```

## Command Line Arguments

- `-k`, `--api-key`: OpenAI API key (overrides environment variable)
- `--unsplash-key`: Unsplash API key (overrides environment variable)
- `-c`, `--category`: News category (e.g., technology, business, politics)
- `-n`, `--count`: Number of news items to generate
- `-o`, `--output`: Custom output JSON filename
- `-s`, `--save`: Save results to JSON file
- `--html`: Generate HTML report
- `--download-images`: Download images locally
- `--image-folder`: Folder to save downloaded images
- `--strapi-url`: Strapi API URL (overrides environment variable)
- `--strapi-token`: Strapi API token (overrides environment variable)
- `--strapi-collection`: Strapi collection type name (default: "articles")
- `--upload-to-strapi`: Upload news items to Strapi
- `--force-fetch`: Force fetching new news even if today's news exists