"""Thin wrappers around the LLM and voice APIs.  OWNER: kate (LLM/voice)"""
import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_flash_v2_5")


def chat_gemini(messages: list[dict], system: str | None = None) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    contents = [
        types.Content(role="model" if m["role"] == "assistant" else "user", parts=[types.Part(text=m["content"])])
        for m in messages
    ]
    config = types.GenerateContentConfig(system_instruction=system) if system else None
    response = client.models.generate_content(model=GEMINI_MODEL, contents=contents, config=config)
    return response.text


def chat_claude(messages: list[dict], system: str | None = None, max_tokens: int = 4000) -> str:
    import anthropic

    client = anthropic.Anthropic()
    kwargs = {"system": system} if system else {}
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        output_config={"effort": "low"},  # short chat replies; keeps latency down
        messages=[{"role": m["role"], "content": m["content"]} for m in messages],
        **kwargs,
    )
    if message.stop_reason == "refusal":
        raise RuntimeError("Claude declined the request")
    return "".join(block.text for block in message.content if block.type == "text")


def chat(messages: list[dict], system: str | None = None) -> str:
    """Multi-turn chat. `messages` is [{"role": "user"|"assistant", "content": str}], starting with a user turn.

    Uses the provider in LLM_PROVIDER and falls back to the other one; raises if both fail.
    """
    providers = [chat_gemini, chat_claude]
    if os.getenv("LLM_PROVIDER", "gemini").lower() == "claude":
        providers.reverse()
    try:
        return providers[0](messages, system)
    except Exception:
        return providers[1](messages, system)


def ask_gemini(prompt: str, system: str | None = None) -> str:
    return chat_gemini([{"role": "user", "content": prompt}], system)


def ask_claude(prompt: str, system: str | None = None) -> str:
    return chat_claude([{"role": "user", "content": prompt}], system)


def ask_llm(prompt: str, system: str | None = None) -> str:
    return chat([{"role": "user", "content": prompt}], system)


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
