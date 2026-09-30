"""Smoke test: one real call to each API. Run: python scripts/hello_apis.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import services  # noqa: E402

PROMPT = "Reply with exactly: hello from KBC"


def check(name, fn):
    try:
        print(f"[OK]   {name}: {fn()}")
        return True
    except Exception as e:
        print(f"[FAIL] {name}: {type(e).__name__}: {e}")
        return False


def hello_voice():
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    audio = services.speak("Hello from KBC.")
    (out / "hello.mp3").write_bytes(audio)
    return f"{len(audio)} bytes -> out/hello.mp3"


results = [
    check(f"Gemini ({services.GEMINI_MODEL})", lambda: services.ask_gemini(PROMPT).strip()),
    check(f"Claude ({services.ANTHROPIC_MODEL})", lambda: services.ask_claude(PROMPT).strip()),
    check(f"ElevenLabs ({services.ELEVENLABS_MODEL})", hello_voice),
]
sys.exit(0 if all(results) else 1)
