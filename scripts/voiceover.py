"""Demo video voiceover: one MP3 per segment + a shot list.

Run: python scripts/voiceover.py            -> out/voiceover/NN_id.mp3 + demo/shotlist.md
     python scripts/voiceover.py --no-audio -> only the shot list (no ElevenLabs key needed)

Edit SEGMENTS to change the narration; keep the whole thing under ~2:50 including the in-app Kate audio.
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

NARRATOR_VOICE_ID = os.getenv("NARRATOR_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")  # George; Kate uses her own voice
NARRATOR_MODEL = os.getenv("NARRATOR_MODEL", "eleven_multilingual_v2")
BYTES_PER_SECOND = 128_000 / 8  # mp3_44100_128

# (id, what to do on screen, narration)
SEGMENTS = [
    ("intro", "Story 1 selected, Lotte, clock on 20 Aug. Slow pan over phone + bank view.",
     "This is Kate, the assistant in KBC Mobile, with one new skill. She reads the signals in your payments "
     "and keeps your insurance and your budget in step with your life. Three customers, three moments."),
    ("moving_quiet", "Stay on 20 Aug. Bank view shows QUIET.",
     "Meet Lotte, twenty-six. In August, nothing unusual. Kate stays quiet."),
    ("moving_signals", "Drag clock to 1 Sep (WATCHING, 62%), pause, then to 30 Sep: Kate card + highlighted rows.",
     "Then: a rental deposit in Ghent. Rent to a new landlord. A van rental. A new internet contract. "
     "One signal means little. Together, Kate is ninety percent sure Lotte is moving, and only then does she "
     "speak up."),
    ("moving_kate", "Talk to Kate → Yes, I'm moving → checklist appears. Hover the tenant fire insurance line.",
     "Kate asks first; she never acts silently. Once Lotte confirms, she gets one checklist, built from her own "
     "products. The big one: in her student room she was covered by someone else's policy. In her new flat she "
     "is not."),
    ("moving_done", "Approve → done screen. Glance at the bank view number.",
     "A dozen admin tasks, done in one tap. And for KBC, the policy stays at the exact moment customers usually "
     "switch."),
    ("trip_ask", "Story 2. Click the 🎤 Normandy question (or speak it). Let Kate's in-app answer play after this line.",
     "Sofie, forty-one, just booked a week in Normandy for the autumn holiday. She simply asks."),
    ("trip_result", "Cover list visible (✅/⚠️). Click Fix it → confirmation.",
     "Kate found the trip from the booking payment and checked it against Sofie's policies. Liability and home: "
     "covered. Medical costs abroad, cancellation and car breakdown: not. Fixed in one tap, before she leaves."),
    ("care_intro", "Story 3, clock on 31 Aug: 'Nothing to flag'. Drag to 30 Sep: strain message + 3 buttons.",
     "Arne, twenty, student in Leuven. In August he's fine, so Kate leaves him alone. Then tuition and kot rent "
     "land in the same month, and he's eight euros short for October."),
    ("care_modes", "Hover over the three mode buttons.",
     "Kate doesn't lecture. She asks how much help he wants: none at all, suggestions he approves, "
     "or do what's best for me."),
    ("care_autopilot", "Click mode 3. Scroll the actions, click one Undo. Then drag clock back to 31 Aug: rules vanish.",
     "On autopilot, rent and bills go first, card payments round up into a buffer, and his unused gym Premium "
     "drops to Basic. Every action is explained, and every action can be undone. When money is healthy again, "
     "the rules switch themselves off."),
    ("scale", "Story 1 bank view → Plug-ins tab (Moving LIVE, baby / car / job PLANNED), then Business impact.",
     "Behind all three is one engine: signals, confidence, actions. Next on the same engine: a new baby, a new "
     "car, a new job. On illustrative assumptions, moving alone protects or wins around twenty-nine thousand "
     "euros of premium per ten thousand customers, every year."),
    ("close", "Back to Lotte's done screen or the KBC Mobile header.",
     "Kate already suggests. With this, she notices, asks, and acts. Kate: one step ahead of your life."),
]


def words_to_seconds(text: str) -> float:
    return len(text.split()) / 2.5  # ~150 words per minute


def main():
    audio = "--no-audio" not in sys.argv
    out = ROOT / "out" / "voiceover"
    out.mkdir(parents=True, exist_ok=True)
    client = None
    if audio:
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

    rows, total = [], 0.0
    for i, (sid, screen, text) in enumerate(SEGMENTS, 1):
        name = f"{i:02d}_{sid}.mp3"
        if client:
            mp3 = b"".join(client.text_to_speech.convert(
                voice_id=NARRATOR_VOICE_ID, model_id=NARRATOR_MODEL, text=text, output_format="mp3_44100_128"))
            (out / name).write_bytes(mp3)
            seconds = len(mp3) / BYTES_PER_SECOND
        else:
            seconds = words_to_seconds(text)
        rows.append(f"| {i} | {total:4.0f}s | {seconds:3.0f}s | {screen} | {text} |")
        total += seconds
        print(f"{name:24} {seconds:5.1f}s")

    kind = "measured from the audio" if client else "estimated at 150 words/min"
    shotlist = "\n".join([
        "# Demo video shot list",
        "",
        f"Narration total: {total:.0f}s ({kind}). Add ~15s for Kate's in-app answer in story 2.",
        "Audio files: out/voiceover/ (not in git; regenerate with `python scripts/voiceover.py`).",
        "",
        "| # | Starts | Length | On screen | Narration |",
        "|---|---|---|---|---|",
        *rows,
    ])
    (ROOT / "demo").mkdir(exist_ok=True)
    (ROOT / "demo" / "shotlist.md").write_text(shotlist + "\n", encoding="utf-8")
    print(f"\nTotal narration {total:.0f}s ({kind}) -> demo/shotlist.md")


if __name__ == "__main__":
    main()
