from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
import time

from audio_processing import load_audio, generate_spectrogram, find_peaks
from fingerprinting import generate_fingerprints
from db_utils import match_fingerprints_time_coherent, get_song_info

app = FastAPI()

AUDIO_FOLDER = "uploaded_audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

THRESHOLD = 10  # matching threshold

@app.post("/match")
async def match_audio(file: UploadFile = File(...)):
    if not file.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only WAV files are accepted.")

    # Save uploaded file locally
    filename = f"upload_{int(time.time())}.wav"
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
    
    # Optionally delete uploaded file after processing
    os.remove(file_path)

    return JSONResponse(content=result)
