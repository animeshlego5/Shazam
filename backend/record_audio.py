import sounddevice as sd
from scipy.io.wavfile import write
import os
import time

def record_audio(duration=5, fs=44100, folder="audio_files"):
    os.makedirs(folder, exist_ok=True)
    filename = f"recorded_audio_{int(time.time())}.wav"
    filepath = os.path.join(folder, filename)
    
    print("Recording started...")
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    
    write(filepath, fs, audio_data)  # Save as WAV file in the folder
    print(f"Recording finished. Audio saved as {filepath}")

if __name__ == "__main__":
    record_audio()
