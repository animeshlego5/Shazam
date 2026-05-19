from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import shutil
import os
import time
import httpx

from audio_processing import load_audio, generate_spectrogram, find_peaks
from fingerprinting import generate_fingerprints
from db_utils import match_fingerprints_time_coherent, get_song_info, insert_song, insert_fingerprints

app = FastAPI()

AUDIO_FOLDER = "uploaded_audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

THRESHOLD = 10  # matching threshold

@app.post("/match")
async def match_audio(file: UploadFile = File(...)):
    if not (file.filename.endswith(".wav") or file.filename.endswith(".mp3")):
        raise HTTPException(status_code=400, detail="Only WAV and MP3 files are accepted.")

    # Save uploaded file locally
    ext = os.path.splitext(file.filename)[1]
    filename = f"upload_{int(time.time())}{ext}"
    file_path = os.path.join(AUDIO_FOLDER, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Load and process audio
    y, sr = load_audio(file_path)
    S_db = generate_spectrogram(y, sr)
    peaks = find_peaks(S_db)
    fingerprints = generate_fingerprints(peaks)

    # Match fingerprints in database
    delta_results, song_best_alignment = match_fingerprints_time_coherent(fingerprints)
    
    sorted_matches = [
        (song_id, count)
        for song_id, count in song_best_alignment.items()
        if count >= THRESHOLD
    ]
    sorted_matches = sorted(sorted_matches, key=lambda x: x[1], reverse=True)

    if sorted_matches:
        best_match_id, best_count = sorted_matches[0]
        title, artist = get_song_info(best_match_id)
        result = {
            "match": True,
            "song_id": best_match_id,
            "title": title,
            "artist": artist,
            "score": best_count
        }
    else:
        result = {
            "match": False,
            "message": "No suitable match found. Please try a longer or clearer audio sample."
        }
    
    # delete uploaded file after processing
    os.remove(file_path)

    return JSONResponse(content=result)

@app.post("/add-song")
async def add_song(
    file: UploadFile, 
    title: str = Form(...), 
    artist: str = Form(...)
):
    # Save file temporarily
    contents = await file.read()
    temp_path = os.path.join(AUDIO_FOLDER, f"temp_{file.filename}")
    with open(temp_path, 'wb') as f:
        f.write(contents)
    
    # Fingerprinting
    y, sr = load_audio(temp_path)
    S_db = generate_spectrogram(y, sr)
    peaks = find_peaks(S_db)
    fingerprints = generate_fingerprints(peaks)
    
    # Insert song & fingerprints
    song_id = insert_song(title, artist)
    insert_fingerprints(song_id, fingerprints)
    
    # Optionally remove temp file
    os.remove(temp_path)
    
    return {"status": "success", "song_id": song_id, "num_fingerprints": len(fingerprints)}

@app.get("/recommendations")
async def get_recommendations(title: str, artist: str):
    # This key should ideally be loaded from an environment variable: os.environ.get("LASTFM_API_KEY")
    # For now, please replace 'YOUR_LASTFM_API_KEY' with the key you just got!
    LAST_FM_API_KEY = os.environ.get("LASTFM_API_KEY", "YOUR_LASTFM_API_KEY")
    
    if LAST_FM_API_KEY == "YOUR_LASTFM_API_KEY":
        raise HTTPException(status_code=500, detail="Last.fm API key is not configured. Please set LASTFM_API_KEY environment variable or hardcode it in api.py.")

    url = f"http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.getsimilar",
        "artist": artist,
        "track": title,
        "api_key": LAST_FM_API_KEY,
        "format": "json",
        "limit": 5,
        "autocorrect": 1
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                raise HTTPException(status_code=400, detail=data.get("message", "Error from Last.fm"))
            
            # Extract relevant info from the response
            similartracks = data.get("similartracks", {}).get("track", [])
            
            recommendations = []
            for track in similartracks:
                recommendations.append({
                    "title": track.get("name"),
                    "artist": track.get("artist", {}).get("name"),
                    "lastfm_url": track.get("url"),
                    "match_score": track.get("match") # a score between 0 and 1
                })
                
            return {"recommendations": recommendations}
            
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"An error occurred while requesting Last.fm: {exc}")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=f"Error response from Last.fm: {exc.response.text}")