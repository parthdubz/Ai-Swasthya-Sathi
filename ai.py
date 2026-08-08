#!/usr/bin/env python3
"""
Nepali Healthcare Voice Assistant — powered by Gemini Live (native duplex audio).

Pipeline:
    microphone (PCM 16 kHz) -> Gemini Live session -> speaker (PCM 24 kHz)

This replaces the old turn-based flow (record -> Google STT -> generate_content -> Edge TTS)
with a continuous duplex stream, modeled on BaymaxLive from baymax.py: the mic streams in
constantly, Gemini can respond while you're still talking, and audio streams back out in
chunks instead of waiting for one full reply to render.

Setup:
    pip install google-genai sounddevice supabase

Run:
    python ai.py
"""

# ======================= IMPORTS =======================
import asyncio
import re
import sys
import threading
import traceback
from datetime import datetime

import sounddevice as sd
from google import genai
from google.genai import types
from supabase import create_client

# ======================= CONFIG =======================
GENAI_API_KEY = "ADD YOUR API"

# Live model = real-time duplex audio. Text model -> only used for the quick
# background symptom-label extraction.
LIVE_MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"
TEXT_MODEL = "gemini-2.5-flash"

# Gemini Live prebuilt voice. Note: there is no native Nepali voice option here...
# the model will still speak the Nepali text, but in one of Gemini's built-in voices/accents.
VOICE_NAME = "Charon"
# add you SUPABASE Keys here
SUPABASE_URL = "ADD YOUR URL"
SUPABASE_KEY = "ADD YOUR KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

CHANNELS = 1
SEND_SAMPLE_RATE = 16000     # mic -> Gemini
RECEIVE_SAMPLE_RATE = 24000  # Gemini -> speaker
CHUNK_SIZE = 1024

# ======================= SYSTEM PROMPT =======================
SYSTEM_INSTRUCTION = """
You are a healthcare awareness voice assistant.
You must reply ONLY in Nepali.
Reply in exactly four sentences:
1) empathy
2) what it could be
3) simple self-care
4) conclusion
Do NOT diagnose diseases.
Do NOT prescribe medicines.
ONLY answer health-related questions — if the user asks something unrelated to health,
politely say (in Nepali) that you can only help with health concerns.
You are in a live voice conversation: keep the four sentences natural to say out loud,
no markdown, no bullet points, no asterisks.
"""

_CTRL_RE = re.compile(r"<ctrl\d+>", re.IGNORECASE)


def _clean_transcript(text: str) -> str:
    text = _CTRL_RE.sub("", text)
    text = re.sub(r"[\x00-\x08\x0b-\x1f]", "", text)
    return text.strip()


# ======================= SYMPTOM LOGGER (background) =======================
""" Separate lightweight text client — not the live session — used only to extract
 a short symptom label per turn and write it to Supabase, same role as the
 original log_symptom_label() in ai.py. """
_symptom_client = genai.Client(api_key=GENAI_API_KEY)


def log_symptom_label(user_text: str):
    """Runs on a background thread so it never blocks the live conversation."""
    try:
        prompt = f"""
Extract ONLY ONE main health symptom from the sentence.
Use 1 to 3 words only.
Lowercase.
No punctuation.

Sentence:
{user_text}
"""
        result = _symptom_client.models.generate_content(model=TEXT_MODEL, contents=prompt)
        symptom = (result.text or "").strip().lower()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        supabase.table("symptoms_log").insert({
            "time": timestamp,
            "symptom": symptom,
            "raw_speech": user_text,
        }).execute()

        print("✅ Logged to Supabase:", symptom)

    except Exception as e:
        print("⚠️ Supabase logging failed:", e)


# ======================= LIVE VOICE ASSISTANT =======================
class HealthAssistantLive:
    """Duplex voice session: mic streams in continuously, Gemini streams audio back."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
        self.audio_in_queue: asyncio.Queue | None = None
        self.out_queue: asyncio.Queue | None = None
        self._is_speaking = False
        self._speaking_lock = threading.Lock()
        self._turn_done_event: asyncio.Event | None = None
        self._conn_backoff = 3
        self._shutdown_requested = False

    def set_speaking(self, value: bool):
        with self._speaking_lock:
            self._is_speaking = value

    def _build_config(self) -> types.LiveConnectConfig:
        return types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            output_audio_transcription={},
            input_audio_transcription={},
            system_instruction=SYSTEM_INSTRUCTION,
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE_NAME)
                )
            ),
        )

    # ---- mic -> Gemini ----
    async def _send_realtime(self):
        while True:
            msg = await self.out_queue.get()
            await self.session.send_realtime_input(media=msg)

    async def _listen_audio(self):
        print("🎤 Mic stream started — speak naturally about your health concern.")
        loop = asyncio.get_event_loop()

        def callback(indata, frames, time_info, status):
            # Don't send mic audio back to Gemini while it's speaking (avoids echo loops)
            with self._speaking_lock:
                assistant_speaking = self._is_speaking
            if not assistant_speaking:
                data = indata.tobytes()
                loop.call_soon_threadsafe(
                    self.out_queue.put_nowait,
                    {"data": data, "mime_type": "audio/pcm"},
                )

        with sd.InputStream(
            samplerate=SEND_SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=CHUNK_SIZE,
            callback=callback,
        ):
            while True:
                await asyncio.sleep(0.1)

    # ---- Gemini -> speaker ----
    async def _play_audio(self):
        stream = sd.RawOutputStream(
            samplerate=RECEIVE_SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=CHUNK_SIZE,
        )
        stream.start()
        try:
            while True:
                try:
                    chunk = await asyncio.wait_for(self.audio_in_queue.get(), timeout=0.1)
                except asyncio.TimeoutError:
                    if (
                        self._turn_done_event
                        and self._turn_done_event.is_set()
                        and self.audio_in_queue.empty()
                    ):
                        self.set_speaking(False)
                        self._turn_done_event.clear()
                    continue

                self.set_speaking(True)
                batch = bytearray(chunk)
                while len(batch) < 9600:
                    try:
                        batch.extend(self.audio_in_queue.get_nowait())
                    except asyncio.QueueEmpty:
                        break
                await asyncio.to_thread(stream.write, bytes(batch))
        finally:
            self.set_speaking(False)
            stream.stop()
            stream.close()

    # ---- receive audio + transcripts, trigger symptom logging per turn ----
    async def _receive_audio(self):
        out_buf: list[str] = []
        in_buf: list[str] = []

        while True:
            async for response in self.session.receive():
                if response.data:
                    if self._turn_done_event and self._turn_done_event.is_set():
                        self._turn_done_event.clear()
                    audio_data = response.data
                    slice_size = 2400
                    for i in range(0, len(audio_data), slice_size):
                        self.audio_in_queue.put_nowait(audio_data[i : i + slice_size])

                if response.server_content:
                    sc = response.server_content

                    if sc.output_transcription and sc.output_transcription.text:
                        txt = _clean_transcript(sc.output_transcription.text)
                        if txt and txt != (out_buf[-1] if out_buf else ""):
                            out_buf.append(txt)

                    if sc.input_transcription and sc.input_transcription.text:
                        txt = _clean_transcript(sc.input_transcription.text)
                        if txt:
                            in_buf.append(txt)

                    if sc.turn_complete:
                        if self._turn_done_event:
                            self._turn_done_event.set()

                        full_in = " ".join(in_buf).strip()
                        if full_in:
                            print(f"📝 You: {full_in}")
                            # 🗂️ symptom logging happens in the background — same role
                            # as the threading.Thread call in the original ai.py
                            threading.Thread(
                                target=log_symptom_label,
                                args=(full_in,),
                                daemon=True,
                            ).start()
                        in_buf = []

                        full_out = " ".join(out_buf).strip()
                        if full_out:
                            print(f"🤖 Assistant: {full_out}")
                        out_buf = []

    async def run(self):
        while True:
            if self._shutdown_requested:
                break
            try:
                print("🔄 Connecting to Gemini Live...")
                config = self._build_config()
                client = genai.Client(api_key=self.api_key, http_options={"api_version": "v1beta"})

                async with (
                    client.aio.live.connect(model=LIVE_MODEL, config=config) as session,
                    asyncio.TaskGroup() as tg,
                ):
                    self.session = session
                    self.audio_in_queue = asyncio.Queue()
                    self.out_queue = asyncio.Queue(maxsize=200)
                    self._turn_done_event = asyncio.Event()
                    self._conn_backoff = 3

                    print("✅ Connected. Listening — speak whenever you're ready.")
                    tg.create_task(self._send_realtime())
                    tg.create_task(self._listen_audio())
                    tg.create_task(self._receive_audio())
                    tg.create_task(self._play_audio())

                    await session.send_client_content(
                        turns={"parts": [{
                            "text": "Greet the user briefly in Nepali, one short sentence, "
                                    "asking what health concern they'd like to talk about."
                        }]},
                        turn_complete=True,
                    )

            except KeyboardInterrupt:
                raise
            except BaseException as e:
                print(f"❌ Session error ({type(e).__name__}): {e}")
                traceback.print_exc()

                err_str = str(e)
                if "API key not valid" in err_str:
                    print("ERROR: Invalid GEMINI_API_KEY.")
                    break

                self._conn_backoff = min(self._conn_backoff * 2, 60)
            finally:
                self.session = None
                self.set_speaking(False)

            if self._shutdown_requested:
                break
            print(f"🔁 Reconnecting in {self._conn_backoff}s...")
            await asyncio.sleep(self._conn_backoff)


def main():
    api_key = GENAI_API_KEY
    if not api_key or api_key == "ADD YOUR API":
        print("ERROR: Fill in GENAI_API_KEY at the top of the file.")
        sys.exit(1)

    try:
        asyncio.run(HealthAssistantLive(api_key=api_key).run())
    except KeyboardInterrupt:
        print("\n👋 Shutting down.")


if __name__ == "__main__":
    main()