import os
import uuid
import yt_dlp
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="."), name="static")

@app.post("/api/download")
async def download_media(request: Request):
    try:
        data = await request.json()
        url = data.get("url")
        format_type = data.get("format") 
        
        file_id = str(uuid.uuid4())
        # Eliminăm extensia strictă pentru a lăsa yt-dlp să aleagă calitatea maximă
        output_template = f"downloads/{file_id}" 

        ydl_opts = {
            'outtmpl': output_template + ".%(ext)s",
            'format': 'bestvideo+bestaudio/best', # Alege automat cea mai bună calitate (4K inclus)
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            },
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
            # yt-dlp va numi fișierul final în funcție de formatul găsit
            filename = ydl.prepare_filename(info)
            
            # Dacă am extras audio, asigurăm extensia .mp3
            if format_type == "audio":
                filename = filename.rsplit('.', 1)[0] + '.mp3'

        return FileResponse(filename, media_type='application/octet-stream', filename=f"rolex-download.{'mp3' if format_type == 'audio' else 'mp4'}")

    except Exception as e:
        return JSONResponse(status_code=400, content={"message": str(e)})

if __name__ == "__main__":
    import uvicorn
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    uvicorn.run(app, host="0.0.0.0", port=8000)
