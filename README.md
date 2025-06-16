# FastAPI Instagram Scraper

This project is a FastAPI application that scrapes Instagram posts using the Apify API. It provides endpoints to retrieve posts from specific URLs, user profiles, and hashtags.

## Project Structure

```
fastapi-instagram-scraper
├── src
│   ├── main.py               # Entry point of the FastAPI application
│   ├── api                   # Contains API routes
│   │   ├── __init__.py
│   │   └── routes
│   │       ├── __init__.py
│   │       └── scraper.py    # Defines API endpoints for scraping
│   ├── services              # Contains business logic for scraping
│   │   ├── __init__.py
│   │   └── instagram_scraper.py # Logic for scraping Instagram posts
│   ├── models                # Contains data models and schemas
│   │   ├── __init__.py
│   │   └── schemas.py        # Data validation and serialization
│   └── utils                 # Utility functions and configurations
│       ├── __init__.py
│       └── config.py         # Configuration settings
├── requirements.txt          # Project dependencies
├── .env                      # Environment variables
├── Dockerfile                # Docker image instructions
└── README.md                 # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/fastapi-instagram-scraper.git
   cd fastapi-instagram-scraper
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables in the `.env` file. Make sure to include your Apify API token.

## Usage

To run the FastAPI application, execute the following command:
```
uvicorn src.main:app --reload
```

You can then access the API at `http://127.0.0.1:8000`.

## API Endpoints

- **Scrape Instagram Posts**: Use the `/scrape` endpoint to scrape posts from specific URLs, user profiles, or hashtags.

## Docker

To build and run the application in a Docker container, use the following commands:
```
docker build -t fastapi-instagram-scraper .
docker run -d -p 8000:8000 fastapi-instagram-scraper
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.