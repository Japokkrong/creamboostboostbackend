# Create app.py in your root directory
# filepath: c:\ig_api_scraper\fastapi-instagram-scraper\app.py
from src.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)