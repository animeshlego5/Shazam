import os
import time
import sounddevice as sd
from scipy.io.wavfile import write
from audio_processing import load_audio, generate_spectrogram, find_peaks
from fingerprinting import generate_fingerprints

AUDIO_FOLDER = "audio_files"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

def select_microphone():
    print("Available input devices:")
    devices = sd.query_devices()
    input_devices = [(i, d['name']) for i, d in enumerate(devices) if d['max_input_channels'] > 0]
    for i, name in input_devices:
        print(f"  [{i}] {name}")
    device_id = int(input("Enter the device ID to use for recording: "))
    print(f"Using device {device_id}: {devices[device_id]['name']}")
    return device_id

def record_audio(filename, duration=10, fs=44100, device=None):
    filepath = os.path.join(AUDIO_FOLDER, filename)
    print(f"Recording {filename}...")
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=device)
    sd.wait()
    write(filepath, fs, audio_data)
    print(f"Saved {filepath}")

# --- Select microphone device ---
device_id = select_microphone()

# --- Record first sample ---
sample1_name = f"sample1_{int(time.time())}.wav"
record_audio(sample1_name, device=device_id)
time.sleep(5)

# --- Record second sample ---
sample2_name = f"sample2_{int(time.time())}.wav"
record_audio(sample2_name, device=device_id)
time.sleep(1)

# --- Process first sample ---
file1_path = os.path.join(AUDIO_FOLDER, sample1_name)
y1, sr1 = load_audio(file1_path)
S_db1 = generate_spectrogram(y1, sr1)
peaks1 = find_peaks(S_db1)
fingerprints1 = generate_fingerprints(peaks1)
print(f"First sample: {len(fingerprints1)} fingerprints.")

# --- Process second sample ---
file2_path = os.path.join(AUDIO_FOLDER, sample2_name)
y2, sr2 = load_audio(file2_path)
S_db2 = generate_spectrogram(y2, sr2)
peaks2 = find_peaks(S_db2)
fingerprints2 = generate_fingerprints(peaks2)
print(f"Second sample: {len(fingerprints2)} fingerprints.")

# --- Local matching logic ---
def simple_match(query_fingerprints, reference_fingerprints, threshold=10):
    query_hashes = set([h for h, t in query_fingerprints])
    ref_hashes = set([h for h, t in reference_fingerprints])
    matched = query_hashes & ref_hashes
    match_count = len(matched)
    return match_count, matched

THRESHOLD = 10
match_count, matched_hashes = simple_match(fingerprints2, fingerprints1, threshold=THRESHOLD)

if match_count >= THRESHOLD:
    print(f"Samples match! {match_count} common fingerprints found.")
else:
    print(f"No suitable match found ({match_count} common fingerprints). Try longer or clearer recordings.")

