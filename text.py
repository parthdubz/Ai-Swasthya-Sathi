import os
import whisper

# Tell Python exactly where ffmpeg.exe is
os.environ["IMAGEIO_FFMPEG_EXE"] = r"C:\ffmpeg\ffmpeg.exe"

# Load a CPU-friendly Whisper model
model = whisper.load_model("tiny")

# Transcribe your audio (WAV or MP3)
result = model.transcribe(r"C:\Users\smart\OneDrive\Desktop\Ai\output.wav")

# Print transcription
print(result["text"])
