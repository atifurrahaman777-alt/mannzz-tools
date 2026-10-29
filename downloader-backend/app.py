import ipaddress
import socket
from urllib.parse import urlparse

import yt_dlp
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mannzz Downloader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mannzz-tools.vercel.app"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

def validate_url(value):
    try:
        parsed = urlparse(value)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            return False

        host = parsed.hostname
        if host.lower() in ("localhost",) or host.endswith(".local"):
            return False

        addresses = socket.getaddrinfo(host, None)
        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])
            if not ip.is_global:
                return False

        return True
    except Exception:
        return False

@app.get("/")
def home():
    return {"status": "online", "service": "Mannzz Downloader"}

@app.get("/api/download")
def download_info(url: str = Query(..., max_length=2048)):
    if not validate_url(url):
        raise HTTPException(status_code=400, detail="URL tidak valid atau bukan alamat publik.")

    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "skip_download": True,
        "format": "best",
        "socket_timeout": 12,
        "extractor_retries": 1,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info or not info.get("url"):
            raise ValueError("Media tidak menyediakan tautan unduhan langsung.")

        return {
            "title": info.get("title") or "Media",
            "thumbnail": info.get("thumbnail"),
            "meta": info.get("duration_string") or info.get("extractor_key") or "",
            "downloadUrl": info["url"],
        }

    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Link tidak didukung, media tidak tersedia, atau situs menolak permintaan."
        )
