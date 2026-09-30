"""Demo video voiceover: one MP3 per segment + a shot list.

Run: python scripts/voiceover.py            -> out/voiceover/NN_id.mp3 + demo/shotlist.md
     python scripts/voiceover.py --no-audio -> only the shot list (no ElevenLabs key needed)

Edit SEGMENTS to change the narration; keep the whole thing under ~2:50 including the in-app Kate audio.
Tone: friendly, calm and reassuring, never salesy.
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

NARRATOR_VOICE_ID = os.getenv("NARRATOR_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")  # Sarah: soft, calm
NARRATOR_MODEL = os.getenv("NARRATOR_MODEL", "eleven_multilingual_v2")
# Higher stability and low style keep the delivery gentle and even; slightly slower than default.
NARRATOR_SETTINGS = {"stability": 0.65, "similarity_boost": 0.75, "style": 0.15, "speed": 0.95}
BYTES_PER_SECOND = 128_000 / 8  # mp3_44100_128
WORDS_PER_SECOND = 140 / 60  # a soft, unhurried pace

# (id, what to do on screen, narration)
SEGMENTS = [
    ("intro", "Story 1 selected, Lotte, clock on 20 Aug. Slow pan over phone + bank view.",
     "Life changes, and the paperwork often lags behind. Kate can help with that. Here are three customers."),
    ("moving_quiet", "Stay on 20 Aug. Bank view shows QUIET.",
     "This is Lotte. She's twenty-six, and in August everything looks calm, so Kate simply lets her be."),
    ("moving_signals", "Drag clock to 1 Sep (WATCHING, 62%), pause, then to 30 Sep: Kate card + highlighted rows.",
     "In September, a rental deposit for a flat in Ghent shows up, then rent to a new landlord and a van rental. "
     "Together, that makes Kate ninety percent sure Lotte is moving, so she reaches out."),
    ("moving_kate", "Talk to Kate → Yes, I'm moving → checklist appears. Hover the tenant fire insurance line.",
     "She asks first, and changes nothing until Lotte says yes. Then she prepares a checklist based on what "
     "Lotte already has. The most important item: in her student room, someone else's policy covered her. "
     "In the new flat, nothing does yet."),
    ("moving_done", "Approve → done screen. Glance at the bank view number.",
     "One tap, and it's taken care of. Lotte can focus on settling in, and her insurance stays with KBC."),
    ("trip_ask", "Story 2. Click the 🎤 Normandy question (or speak it). Let Kate's in-app answer play after this line.",
     "Sofie is getting ready for a week in Normandy with her family. She just asks Kate if they're covered."),
    ("trip_result", "Cover list visible (✅/⚠️). Click Fix it → confirmation.",
     "Kate had already spotted the trip in her payments. Their liability and home insurance are fine, but "
     "medical costs abroad, cancelling the booking and car trouble on the way aren't covered yet. Sofie can "
     "fix that in one tap before they leave."),
    ("care_intro", "Story 3, clock on 31 Aug: 'Nothing to flag'. Drag to 30 Sep: strain message + 3 buttons.",
     "Arne is a student in Leuven. Over the summer, Kate leaves him in peace. In September, tuition and his "
     "kot rent arrive at the same time, and he's eight euros short for October."),
    ("care_modes", "Hover over the three mode buttons.",
     "Kate doesn't judge. She asks how much help he'd like: no tips at all, suggestions he approves himself, "
     "or letting her take care of it."),
    ("care_autopilot", "Click mode 3. Scroll the actions, click one Undo. Then drag clock back to 31 Aug: rules vanish.",
     "He lets her take care of it. His rent is set aside first, small round-ups build a little buffer, and his "
     "gym moves to a cheaper plan. Every change is explained and can be undone, and once he's back on his feet, "
     "Kate steps back."),
    ("scale", "Story 1 bank view → Plug-ins tab (Moving LIVE, baby / car / job PLANNED), then Business impact.",
     "The same approach can help with a new baby, a new car or a new job. On our first assumptions, moving "
     "alone keeps or wins about twenty-nine thousand euros in premiums a year per ten thousand customers."),
    ("close", "Back to Lotte's done screen or the KBC Mobile header.",
     "Kate already gives good advice. With this, she can quietly take care of the follow-up too, whenever "
     "you're ready."),
]


def main():
    audio = "--no-audio" not in sys.argv
    out = ROOT / "out" / "voiceover"
    out.mkdir(parents=True, exist_ok=True)
    client = None
    if audio:
        from elevenlabs import VoiceSettings
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
        settings = VoiceSettings(**NARRATOR_SETTINGS)

    rows, total = [], 0.0
    for i, (sid, screen, text) in enumerate(SEGMENTS, 1):
        name = f"{i:02d}_{sid}.mp3"
        if client:
            mp3 = b"".join(client.text_to_speech.convert(
                voice_id=NARRATOR_VOICE_ID, model_id=NARRATOR_MODEL, text=text, voice_settings=settings,
                output_format="mp3_44100_128"))
            (out / name).write_bytes(mp3)
            seconds = len(mp3) / BYTES_PER_SECOND
        else:
            seconds = len(text.split()) / WORDS_PER_SECOND
        rows.append(f"| {i} | {total:4.0f}s | {seconds:3.0f}s | {screen} | {text} |")
        total += seconds
        print(f"{name:24} {seconds:5.1f}s")

    kind = "measured from the audio" if client else "estimated at 140 words/min"
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
