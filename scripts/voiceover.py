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
     "We built an extension for Kate that uses what happens in your payments to keep your insurance and "
     "budget up to date. Three customers."),
    ("moving_quiet", "Stay on 20 Aug. Bank view shows QUIET.",
     "Lotte is twenty-six. In August her payments look normal, so Kate doesn't say anything."),
    ("moving_signals", "Drag clock to 1 Sep (WATCHING, 62%), pause, then to 30 Sep: Kate card + highlighted rows.",
     "In September there's a rental deposit for a flat in Ghent, rent to a new landlord and a van rental. "
     "Together, Kate is ninety percent sure Lotte is moving, and that's when she speaks up."),
    ("moving_kate", "Talk to Kate → Yes, I'm moving → checklist appears. Hover the tenant fire insurance line.",
     "She asks before she changes anything. Once Lotte says yes, Kate puts together a checklist based on the "
     "products Lotte actually has. The one that matters most is fire insurance. In her student room someone "
     "else's policy covered her. In the new flat, nothing does."),
    ("moving_done", "Approve → done screen. Glance at the bank view number.",
     "Lotte approves it in one go. For KBC, this is usually the moment a customer takes their insurance "
     "somewhere else."),
    ("trip_ask", "Story 2. Click the 🎤 Normandy question (or speak it). Let Kate's in-app answer play after this line.",
     "Sofie is forty-one and just booked a week in Normandy for the autumn holiday. She asks Kate if they're "
     "covered."),
    ("trip_result", "Cover list visible (✅/⚠️). Click Fix it → confirmation.",
     "Kate already knew about the trip from the booking payment. Their liability and home insurance are fine. "
     "Medical costs abroad, cancelling the booking and a breakdown on the way there aren't covered, and Sofie "
     "can sort that out before they leave."),
    ("care_intro", "Story 3, clock on 31 Aug: 'Nothing to flag'. Drag to 30 Sep: strain message + 3 buttons.",
     "Arne is a student in Leuven. In August, Kate leaves him alone. In September, tuition and kot rent hit in "
     "the same month, and he's eight euros short for October's rent."),
    ("care_modes", "Hover over the three mode buttons.",
     "Kate asks how involved he wants her to be. He can turn the tips off, approve her suggestions one by one, "
     "or let her handle it."),
    ("care_autopilot", "Click mode 3. Scroll the actions, click one Undo. Then drag clock back to 31 Aug: rules vanish.",
     "He lets her handle it. Rent money is kept aside first, card payments round up into a small buffer, and "
     "his gym goes from Premium to Basic, since he only uses one club. Each change comes with a reason and an "
     "undo button. Once his balance recovers, the rules stop."),
    ("scale", "Story 1 bank view → Plug-ins tab (Moving LIVE, baby / car / job PLANNED), then Business impact.",
     "Next we'd add a new baby, a new car and a new job to the same rules. On assumptions we'd still check "
     "against KBC's data, moving alone keeps or wins about twenty-nine thousand euros in premiums a year per "
     "ten thousand customers."),
    ("close", "Back to Lotte's done screen or the KBC Mobile header.",
     "Today Kate sends suggestions. With this extension, she can also follow through on them, once the "
     "customer says yes."),
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
