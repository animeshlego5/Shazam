import numpy as np
import librosa
import matplotlib.pyplot as plt
from scipy.ndimage import maximum_filter

def load_audio(file_path):
    y, sr = librosa.load(file_path, sr=None, mono=True)
    return y, sr

def generate_spectrogram(y, sr, n_fft=2048, hop_length=512):
    # Create magnitude spectrogram in decibels
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    S_db = librosa.amplitude_to_db(S, ref=np.max)
    return S_db

def find_peaks(S_db, neighborhood_size=20, amp_min=-40):
    # Identify local maxima in spectrogram above amplitude threshold
    max_filtered = maximum_filter(S_db, size=neighborhood_size)
    peaks = np.argwhere((S_db == max_filtered) & (S_db > amp_min))
    return peaks

def plot_spectrogram(S_db, peaks=None):
    plt.figure(figsize=(12, 6))
    plt.imshow(S_db, origin='lower', aspect='auto', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    if peaks is not None:
        y, x = zip(*peaks)
        plt.scatter(x, y, marker='o', color='cyan', s=15)
    plt.title('Spectrogram with Peaks')
    plt.xlabel('Time frame')
    plt.ylabel('Frequency bin')
    plt.show()
