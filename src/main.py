from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.routes.scraper import router as scraper_router

app = FastAPI(
    title="Instagram Profile Scraper API",
    description="API for scraping Instagram profiles and their posts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods including OPTIONS
    allow_headers=["*"],  # Allows all headers
)

app.include_router(scraper_router, prefix="/api/v1", tags=["scraper"])

@app.get("/")
async def root():
    return {"message": "Instagram Profile Scraper API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)