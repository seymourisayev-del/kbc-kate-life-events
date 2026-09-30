"""Join the 12 narration clips into one track with pauses for clicking.

Run after scripts/voiceover.py:  python scripts/voiceover_full.py  (needs: pip install imageio-ffmpeg)
Output: out/voiceover/narration_full.mp3 + the second each clip starts, to click along while recording.
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

sys.path.insert(0, str(Path(__file__).resolve().parent))
from voiceover import BYTES_PER_SECOND, SEGMENTS  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "out" / "voiceover"
# Silence after each clip (seconds): time to click; long gap after clip 6 for Kate's own spoken answer.
PAUSE_AFTER = {"moving_signals": 2.5, "moving_kate": 1.5, "trip_ask": 17.0, "care_intro": 2.0,
               "care_autopilot": 2.0, "scale": 1.0}
DEFAULT_PAUSE = 1.0


def main():
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    inputs, filters, t = [], [], 0.0
    for i, (sid, screen, _) in enumerate(SEGMENTS, 1):
        clip = OUT / f"{i:02d}_{sid}.mp3"
        pause = PAUSE_AFTER.get(sid, DEFAULT_PAUSE)
        print(f"{int(t // 60)}:{t % 60:04.1f}  clip {i:2d}  -> {screen}")
        t += clip.stat().st_size / BYTES_PER_SECOND + pause
        inputs += ["-i", str(clip)]
        filters.append(f"[{i - 1}:a]apad=pad_dur={pause}[a{i}]")
    joined = "".join(f"[a{i}]" for i in range(1, len(SEGMENTS) + 1))
    graph = ";".join(filters) + f";{joined}concat=n={len(SEGMENTS)}:v=0:a=1[out]"
    target = OUT / "narration_full.mp3"
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", *inputs, "-filter_complex", graph, "-map", "[out]",
                    "-b:a", "128k", str(target)], check=True)
    print(f"\n{int(t // 60)}:{t % 60:04.1f} total -> {target}")


if __name__ == "__main__":
    main()
