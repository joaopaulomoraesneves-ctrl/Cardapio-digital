import os
import re
import urllib.parse
from typing import Optional, Generator
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import yt_dlp

app = FastAPI(title="Video Downloader API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoInfoRequest(BaseModel):
    url: str

def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    name = name.replace('\n', ' ').replace('\r', '').strip()
    return name[:200] if name else "video"

def get_yt_dlp_options():
    return {
        'quiet': True,
        'no_warnings': True,
        'no_color': True,
        'extract_flat': False,
        'format': 'best',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    }

@app.post("/api/info")
def extract_info(req: VideoInfoRequest):
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL inválida")

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    ydl_opts = get_yt_dlp_options()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise HTTPException(status_code=400, detail="Não foi possível obter informações do vídeo")

            # Handle playlists if a single video was not extracted directly
            if '_type' in info and info['_type'] == 'playlist':
                entries = list(info.get('entries', []))
                if entries:
                    info = entries[0]
                else:
                    raise HTTPException(status_code=400, detail="Nenhum vídeo encontrado no link informado")

            title = info.get('title') or "Vídeo sem título"
            thumbnail = info.get('thumbnail') or ""
            duration = info.get('duration') or 0
            uploader = info.get('uploader') or info.get('extractor_key') or "Desconhecido"
            extractor = info.get('extractor_key') or info.get('extractor') or "Website"

            formats_list = []
            seen_combos = set()

            raw_formats = info.get('formats', [])
            if not raw_formats and info.get('url'):
                # Single format video (like direct mp4 or simple extractors)
                raw_formats = [{
                    'format_id': 'direct',
                    'ext': info.get('ext', 'mp4'),
                    'url': info.get('url'),
                    'format_note': 'Padrão',
                    'filesize': info.get('filesize') or info.get('filesize_approx')
                }]

            for f in raw_formats:
                download_url = f.get('url')
                if not download_url:
                    continue

                ext = f.get('ext') or 'mp4'
                format_id = f.get('format_id', 'best')
                height = f.get('height')
                width = f.get('width')
                vcodec = f.get('vcodec') or ''
                acodec = f.get('acodec') or ''
                filesize = f.get('filesize') or f.get('filesize_approx') or 0

                res_label = ""
                if height:
                    res_label = f"{height}p"
                elif f.get('format_note'):
                    res_label = f.get('format_note')
                elif vcodec == 'none' and acodec != 'none':
                    res_label = "Apenas Áudio"
                else:
                    res_label = "Padrão"

                is_audio_only = (vcodec == 'none' and acodec != 'none')
                is_video_with_audio = (vcodec != 'none' and acodec != 'none')

                combo_key = f"{res_label}_{ext}_{is_audio_only}"

                # Prefer formats with audio+video or standalone clean audio
                formats_list.append({
                    'format_id': format_id,
                    'ext': ext,
                    'resolution': res_label,
                    'filesize': filesize,
                    'has_audio': acodec != 'none',
                    'has_video': vcodec != 'none',
                    'note': f.get('format_note', ''),
                    'download_url': download_url
                })

            # Sort formats: combined video+audio first (by height desc), then audio-only
            def sort_key(item):
                res_num = 0
                if item['resolution'].endswith('p') and item['resolution'][:-1].isdigit():
                    res_num = int(item['resolution'][:-1])
                score = 0
                if item['has_video'] and item['has_audio']:
                    score = 10000 + res_num
                elif item['has_video']:
                    score = 5000 + res_num
                elif item['has_audio']:
                    score = 1000
                return score

            formats_list.sort(key=sort_key, reverse=True)

            return {
                'title': title,
                'thumbnail': thumbnail,
                'duration': duration,
                'uploader': uploader,
                'site': extractor,
                'formats': formats_list[:25],  # Top formats
                'webpage_url': info.get('webpage_url', url)
            }
    except Exception as e:
        # Fallback for direct media links (.mp4, .m3u8, .webm, .mp3, etc.)
        if any(url.lower().endswith(ext) or ext in url.lower() for ext in ['.mp4', '.mkv', '.webm', '.mov', '.mp3', '.m4a']):
            filename = url.split('/')[-1].split('?')[0] or "video.mp4"
            return {
                'title': filename,
                'thumbnail': '',
                'duration': 0,
                'uploader': 'Link Direto',
                'site': 'Link Direto',
                'formats': [{
                    'format_id': 'direct',
                    'ext': filename.split('.')[-1] if '.' in filename else 'mp4',
                    'resolution': 'Original',
                    'filesize': 0,
                    'has_audio': True,
                    'has_video': True,
                    'note': 'Link direto de mídia',
                    'download_url': url
                }],
                'webpage_url': url
            }
        raise HTTPException(status_code=400, detail=f"Erro ao extrair vídeo: {str(e)}")


@app.get("/api/download")
def download_stream(
    url: str = Query(...),
    format_id: Optional[str] = Query("best"),
    filename: Optional[str] = Query(None)
):
    if not url:
        raise HTTPException(status_code=400, detail="URL necessária")

    ydl_opts = get_yt_dlp_options()
    download_target_url = None
    file_ext = "mp4"
    title = filename or "video"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info:
                title = filename or info.get('title') or "video"
                formats = info.get('formats', [])

                target_format = None
                if format_id and format_id != 'direct':
                    for f in formats:
                        if f.get('format_id') == format_id:
                            target_format = f
                            break

                if not target_format and formats:
                    # Pick best combined format or first format with url
                    for f in reversed(formats):
                        if f.get('url') and f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                            target_format = f
                            break
                    if not target_format:
                        target_format = formats[-1]

                if target_format:
                    download_target_url = target_format.get('url')
                    file_ext = target_format.get('ext') or 'mp4'
                else:
                    download_target_url = info.get('url')
                    file_ext = info.get('ext') or 'mp4'
    except Exception:
        # Fallback to URL as direct media link
        download_target_url = url
        if '.' in url.split('/')[-1]:
            file_ext = url.split('/')[-1].split('?')[0].split('.')[-1]

    if not download_target_url:
        raise HTTPException(status_code=400, detail="Não foi possível obter o link de download direto.")

    clean_filename = sanitize_filename(title) + f".{file_ext}"
    encoded_filename = urllib.parse.quote(clean_filename)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        req_stream = requests.get(download_target_url, headers=headers, stream=True, timeout=15)
        content_type = req_stream.headers.get('Content-Type', 'application/octet-stream')
        content_length = req_stream.headers.get('Content-Length')

        def iterfile() -> Generator[bytes, None, None]:
            try:
                for chunk in req_stream.iter_content(chunk_size=1024 * 1024): # 1MB chunks
                    if chunk:
                        yield chunk
            finally:
                req_stream.close()

        res_headers = {
            "Content-Disposition": f"attachment; filename=\"{clean_filename}\"; filename*=UTF-8''{encoded_filename}"
        }
        if content_length:
            res_headers["Content-Length"] = content_length

        return StreamingResponse(
            iterfile(),
            media_type=content_type,
            headers=res_headers
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao transmitir vídeo: {str(e)}")


app.mount("/", StaticFiles(directory=".", html=True), name="static")
