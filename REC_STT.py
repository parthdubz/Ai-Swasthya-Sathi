import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import whisper
import time
import os

# ===== SETTINGS =====
DURATION = 30        # seconds per chunk
SAMPLE_RATE = 16000 # Whisper prefers 16kHz
LANGUAGE = "ne"     # Nepali
MODEL_SIZE = "base" # small / medium = better accuracy

# ====================

model = whisper.load_model(MODEL_SIZE)

def record_chunk(filename):
    print("🎙️ Recording...")
    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype=np.int16
    )
    sd.wait()
    wav.write(filename, SAMPLE_RATE, audio)
    print("✅ Saved:", filename)

def transcribe_chunk(filename):
    result = model.transcribe(filename, language=LANGUAGE)
    return result["text"]

chunk = 1

while True:
    file = f"chunk_{chunk}.wav"

    record_chunk(file)
    text = transcribe_chunk(file)

    print(f"\n📝 Chunk {chunk} Transcription:")
    print(text)
    print("-" * 40)

    os.remove(file)  # optional: delete audio after processing
    chunk += 1
