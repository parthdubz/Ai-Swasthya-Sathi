import sounddevice as sd
import numpy as np
import soundfile as sf

MIC_INDEX = 9
CHANNELS = 1

device_info = sd.query_devices(MIC_INDEX, 'input')
SAMPLE_RATE = int(device_info['default_samplerate'])
print(f"Using sample rate: {SAMPLE_RATE}")

DURATION = 30 # seconds per chunk
all_audio = []

def callback(indata, frames, time, status):
    if status:
        print(status)
    all_audio.append(indata.copy())

with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, device=MIC_INDEX, callback=callback):
    sd.sleep(DURATION * 1000)  # capture for DURATION seconds

# Convert list of arrays to single numpy array
audio_np = np.concatenate(all_audio, axis=0)

# Save as WAV
sf.write("output.wav", audio_np, SAMPLE_RATE)
print("Saved output.wav")
