"""
transcribe.py — real speech-to-text via Groq's Whisper endpoint.
This is what SpeechRecording.jsx will eventually call instead of its
current placeholder text.
"""

import os
from dotenv import load_dotenv
from langfuse.openai import OpenAI  # traced, same pattern as everywhere else
from langfuse import observe

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# turbo = faster, slightly less accurate than plain whisper-large-v3.
# Worth the tradeoff here since this is an interactive rehearsal tool,
# not a batch transcription job — latency matters more than perfect
# accuracy on every word.
MODEL = "whisper-large-v3-turbo"


@observe(name="transcribe-audio")
def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    audio_bytes: raw audio file bytes (webm, mp3, wav, m4a, etc. — Groq
    supports all of these directly, no conversion needed).
    filename: needs a real extension so Groq can detect the format —
    the bytes alone don't carry that information.
    """
    import io
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename  # the SDK reads this to infer format

    transcript = client.audio.transcriptions.create(
        model=MODEL,
        file=audio_file,
    )
    return transcript.text