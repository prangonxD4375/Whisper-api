# Self-hosted Whisper API clone using FastAPI.
# Handles audio file uploads, transcribes with Whisper, translates to selected language,
# and returns results as downloadable files or JSON.

import sys
import tempfile
import os
import shutil
import subprocess

try:
    import ssl
except ModuleNotFoundError:
    raise RuntimeError("Python environment missing SSL support. Rebuild Python with OpenSSL.")

ffmpeg_path = r"C:/Users/User/AppData/Local/Microsoft/WinGet/Links/ffmpeg"
try:
    subprocess.run([ffmpeg_path, "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.environ["PATH"] = f"{os.path.dirname(ffmpeg_path)};{os.environ['PATH']}"
except Exception:
    raise RuntimeError("ffmpeg executable is not functional. Please verify your ffmpeg installation and path.")

try:
    import whisper
    WHISPER_AVAILABLE = True
except ModuleNotFoundError:
    WHISPER_AVAILABLE = False

from fastapi import FastAPI, UploadFile, BackgroundTasks, Request, Query, Form
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from transformers import MarianMTModel, MarianTokenizer

app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

model = whisper.load_model("base") if WHISPER_AVAILABLE else None
TRANSLATORS = {}

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    lang_code = f"{source_lang}->{target_lang}"
    if lang_code not in TRANSLATORS:
        tokenizer = MarianTokenizer.from_pretrained(f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}")
        model = MarianMTModel.from_pretrained(f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}")
        TRANSLATORS[lang_code] = (tokenizer, model)
    else:
        tokenizer, model = TRANSLATORS[lang_code]

    tokens = tokenizer([text], return_tensors="pt", padding=True, truncation=True)
    translated = model.generate(**tokens)
    return tokenizer.batch_decode(translated, skip_special_tokens=True)[0]

def format_srt(segments):
    def to_timestamp(seconds):
        ms = int((seconds - int(seconds)) * 1000)
        return f"{int(seconds // 3600):02}:{int((seconds % 3600) // 60):02}:{int(seconds % 60):02},{ms:03}"

    srt = ""
    for i, seg in enumerate(segments, 1):
        start = to_timestamp(seg['start'])
        end = to_timestamp(seg['end'])
        srt += f"{i}\n{start} --> {end}\n{seg['text'].strip()}\n\n"
    return srt

def format_vtt(segments):
    def to_timestamp(seconds):
        ms = int((seconds - int(seconds)) * 1000)
        return f"{int(seconds // 3600):02}:{int((seconds % 3600) // 60):02}:{int(seconds % 60):02}.{ms:03}"

    vtt = "WEBVTT\n\n"
    for seg in segments:
        start = to_timestamp(seg['start'])
        end = to_timestamp(seg['end'])
        vtt += f"{start} --> {end}\n{seg['text'].strip()}\n\n"
    return vtt

@app.post("/transcribe-ui")
async def transcribe_ui(file: UploadFile, format: str = Form("srt"), lang: str = Form("en")):
    return await transcribe_audio_ui(file, format, lang)

async def transcribe_audio_ui(file: UploadFile, format: str, lang: str):
    if not WHISPER_AVAILABLE:
        return JSONResponse(status_code=503, content={"error": "Whisper is not installed."})

    try:
        file_content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        result = model.transcribe(tmp_path)
        source_lang = result.get("language", "en")
        segments = result.get("segments", [])
        os.unlink(tmp_path)

        if lang != source_lang:
            for seg in segments:
                seg['text'] = translate_text(seg['text'], source_lang, lang)

        if format == "srt":
            content = format_srt(segments)
            return PlainTextResponse(content=content, media_type="text/plain")
        elif format == "vtt":
            content = format_vtt(segments)
            return PlainTextResponse(content=content, media_type="text/vtt")
        else:
            return JSONResponse(content={
                "text": result.get("text", ""),
                "srt": format_srt(segments),
                "vtt": format_vtt(segments)
            })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
