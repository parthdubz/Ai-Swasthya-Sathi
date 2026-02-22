# ======================= IMPORTS =======================
import speech_recognition as sr
import google.generativeai as genai
import edge_tts
import asyncio
import os
import threading
from datetime import datetime
from supabase import create_client

# ======================= CONFIG =======================
GENAI_API_KEY = "AIzaSyCTq9izH8ozVBrPuqQ8RTFnsYrMiMO5Vj4"
GENAI_MODEL = "gemini-2.5-flash"

VOICE = "ne-NP-SagarNeural"
TTS_FILE = "reply.mp3"

WAITING_REPLY = "ठीक छ, म केही सेकेन्डमा जवाफ दिनेछु।"

SUPABASE_URL = "https://jclnnbllracsxhbukxhy.supabase.co"
SUPABASE_KEY = "sb_publishable_FKVTJrNZeY0Vz6tVaUWNQA_v9wXRADk"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ======================= SYSTEM PROMPT =======================
SYSTEM_PROMPT = """
You are a healthcare awareness assistant.
You must reply ONLY in Nepali.
Reply in exactly four sentences:
1) empathy
2) what it could be
3) simple self-care
4) conclusion
Do NOT diagnose diseases.
Do NOT prescribe medicines.
ONLY answer health-related questions.
"""

# ======================= INIT =======================
print("🔄 Initializing Gemini...")
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel(GENAI_MODEL)

print("🔄 Initializing speech recognition...")
recognizer = sr.Recognizer()
mic = sr.Microphone()

print("✅ System Ready — Press 'y' to start speaking")

# ======================= TTS =======================
async def speak_async(text):
    communicate = edge_tts.Communicate(text=text, voice=VOICE)
    await communicate.save(TTS_FILE)
    os.startfile(TTS_FILE)

def speak(text):
    asyncio.run(speak_async(text))

# ======================= SYMPTOM LOGGER =======================
def log_symptom_label(user_text):
    try:
        prompt = f"""
Extract ONLY ONE main health symptom from the sentence.
Use 1 to 3 words only.
Lowercase.
No punctuation.

Sentence:
{user_text}
"""
        result = model.generate_content(prompt)
        symptom = result.text.strip().lower()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        supabase.table("symptoms_log").insert({
            "time": timestamp,
            "symptom": symptom,
            "raw_speech": user_text
        }).execute()

        print("✅ Logged to Supabase:", symptom)

    except Exception as e:
        print("⚠️ Supabase logging failed:", e)

# ======================= LISTEN =======================
def listen(timeout=None):
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        audio = recognizer.listen(source, timeout=timeout)
    return recognizer.recognize_google(audio).lower()

# ======================= MAIN LOOP =======================
while True:
    try:
        start = input("\nPress 'y' and Enter to speak your health concern: ").strip().lower()
        if start != 'y':
            continue

        print("🎤 Listening...")
        user_text = listen(timeout=6)
        print("📝 User:", user_text)

        # 🔊 Instant feedback (NO LAG FEEL)
        threading.Thread(
            target=speak,
            args=(WAITING_REPLY,),
            daemon=True
        ).start()

        # 🤖 Gemini processing
        prompt = SYSTEM_PROMPT + "\nUser:\n" + user_text
        response = model.generate_content(prompt)
        reply = response.text.strip()

        print("🤖 AI (Nepali):", reply)

        # 🗂️ Log symptom (background)
        threading.Thread(
            target=log_symptom_label,
            args=(user_text,),
            daemon=True
        ).start()

        # 🔊 Final reply
        speak(reply)

    except sr.UnknownValueError:
        print("⚠️ Audio samajh nahi aaya, dobara try karo.")
    except Exception as e:
        print("❌ Error:", e)
