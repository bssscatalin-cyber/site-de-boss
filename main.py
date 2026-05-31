import os
import uuid
import yt_dlp
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the index.html from the root directory
app.mount("/static", StaticFiles(directory="."), name="static")

@app.post("/api/download")
async def download_media(request: Request):
    try:
        data = await request.json()
        url = data.get("url")
        format_type = data.get("format") # 'video' or 'audio'
        
        # Generate a unique ID for the file to prevent overwriting
        file_id = str(uuid.uuid4())
        output_template = f"downloads/{file_id}.%(ext)s"

        ydl_opts = {
            'outtmpl': output_template,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        }
        
        if format_type == "audio":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # If converted to mp3, update filename extension
            if format_type == "audio":
                filename = filename.rsplit('.', 1)[0] + '.mp3'

        return FileResponse(filename, media_type='application/octet-stream', filename=f"made-by-rolex.{'mp3' if format_type == 'audio' else 'mp4'}")

    except Exception as e:
        return JSONResponse(status_code=400, content={"message": str(e)})

if __name__ == "__main__":
    import uvicorn
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    uvicorn.run(app, host="0.0.0.0", port=8000)