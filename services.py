"""Thin wrappers around the LLM and voice APIs. Import these from app.py."""
import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_flash_v2_5")


def ask_gemini(prompt: str, system: str | None = None) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    config = types.GenerateContentConfig(system_instruction=system) if system else None
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt, config=config)
    return response.text


def ask_claude(prompt: str, system: str | None = None, max_tokens: int = 2000) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    kwargs = {"system": system} if system else {}
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
        **kwargs,
    )
    return "".join(block.text for block in message.content if block.type == "text")


def ask_llm(prompt: str, system: str | None = None) -> str:
    """Route to the provider set in LLM_PROVIDER, falling back to the other one on failure."""
    providers = [ask_gemini, ask_claude]
    if os.getenv("LLM_PROVIDER", "gemini").lower() == "claude":
        providers.reverse()
    try:
        return providers[0](prompt, system)
    except Exception:
        return providers[1](prompt, system)


def speak(text: str) -> bytes:
    """Return MP3 bytes; pass straight to st.audio(..., format='audio/mpeg')."""
    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    audio = client.text_to_speech.convert(
        voice_id=ELEVENLABS_VOICE_ID,
        model_id=ELEVENLABS_MODEL,
        text=text,
        output_format="mp3_44100_128",
    )
    return b"".join(audio)
