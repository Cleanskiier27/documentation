import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="NetworkBuster YouTube Trends Service")

# YouTube API Key from environment or placeholder
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_API_KEY_HERE")
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos"

class VideoTrend(BaseModel):
    id: str
    title: str
    thumbnail: str
    channelTitle: str
    viewCount: Optional[str] = "0"
    videoUrl: str

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
        <head>
            <title>YouTube Trends - NetworkBuster</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #121212; color: #e0e0e0; padding: 40px; }
                h1 { color: #ff0000; text-align: center; }
                .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 25px; margin-top: 30px; }
                .card { background: #1e1e1e; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5); transition: transform 0.3s; }
                .card:hover { transform: translateY(-5px); }
                .card img { width: 100%; height: auto; }
                .card-content { padding: 15px; }
                .card-title { font-size: 1.1em; font-weight: bold; margin-bottom: 10px; height: 2.4em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
                .card-channel { color: #aaaaaa; font-size: 0.9em; }
                .card-views { color: #888888; font-size: 0.8em; margin-top: 5px; }
                a { text-decoration: none; color: inherit; }
                .nav { text-align: center; margin-bottom: 20px; }
                .nav a { color: #4dabf7; margin: 0 10px; }
            </style>
        </head>
        <body>
            <div class="nav">
                <a href="/">Home</a> | <a href="/api/trends">JSON API</a>
            </div>
            <h1>🎥 YouTube Trending Videos</h1>
            <div id="trends-grid" class="grid">
                <p style="text-align:center; width:100%;">Loading trends...</p>
            </div>
            <script>
                async function loadTrends() {
                    try {
                        const response = await fetch('/api/trends');
                        const data = await response.json();
                        const grid = document.getElementById('trends-grid');
                        grid.innerHTML = data.map(video => `
                            <a href="${video.videoUrl}" target="_blank">
                                <div class="card">
                                    <img src="${video.thumbnail}" alt="${video.title}">
                                    <div class="card-content">
                                        <div class="card-title">${video.title}</div>
                                        <div class="card-channel">${video.channelTitle}</div>
                                        <div class="card-views">${Number(video.viewCount).toLocaleString()} views</div>
                                    </div>
                                </div>
                            </a>
                        `).join('');
                    } catch (error) {
                        document.getElementById('trends-grid').innerHTML = '<p>Error loading trends. Make sure YOUTUBE_API_KEY is set.</p>';
                    }
                }
                loadTrends();
            </script>
        </body>
    </html>
    """

@app.get("/api/trends", response_model=List[VideoTrend])
async def get_trends(region_code: str = "US", max_results: int = 12):
    if YOUTUBE_API_KEY == "YOUR_API_KEY_HERE":
        # Mock data for demonstration if no API key
        return [
            VideoTrend(
                id="dQw4w9WgXcQ",
                title="Rick Astley - Never Gonna Give You Up (Official Music Video)",
                thumbnail="https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
                channelTitle="Rick Astley",
                viewCount="1500000000",
                videoUrl="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            ),
            VideoTrend(
                id="jNQXAC9IVRw",
                title="Me at the zoo",
                thumbnail="https://i.ytimg.com/vi/jNQXAC9IVRw/hqdefault.jpg",
                channelTitle="jawed",
                viewCount="300000000",
                videoUrl="https://www.youtube.com/watch?v=jNQXAC9IVRw"
            )
        ]

    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region_code,
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(YOUTUBE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            trends = []
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                statistics = item.get("statistics", {})
                trends.append(VideoTrend(
                    id=item["id"],
                    title=snippet.get("title", ""),
                    thumbnail=snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                    channelTitle=snippet.get("channelTitle", ""),
                    viewCount=statistics.get("viewCount", "0"),
                    videoUrl=f"https://www.youtube.com/watch?v={item['id']}"
                ))
            return trends
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
