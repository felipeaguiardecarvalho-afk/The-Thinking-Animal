#!/usr/bin/env python3
"""Generate real image-to-video animation via Gemini Veo 3.1 (same pipeline as Gemini app)."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from google import genai
from google.genai import types

DEFAULT_IMAGE = Path(
    "/home/ubuntu/.cursor/projects/workspace/assets/9241a1f2-4b81-44b3-a3d4-48641fcbd48c.jpg"
)
DEFAULT_OUT = Path("/opt/cursor/artifacts/total_desprepato_animation.mp4")

MOTION_PROMPT = """
Animate this exact 1980s heavy-metal comic-book illustration as a single continuous shot.
Preserve Desprepato's original appearance, the yellow padded couch and room, wall chains,
overhead caged lamp, and the TOTAL DESPREPARO logo exactly — no redesign, no new text, no dialogue.

Style: explosive, darkly humorous, aggressive visual rhythm; hand-drawn comic motion with strong
impact moments, dramatic shadows, and subtle camera shake only during thrashing (not a sliding still image).

Beat structure (~8 seconds):
0) Desprepato already furious, sweating, heavy breathing in the straitjacket on the yellow couch.
1) Violent thrashing — body and orange webbed feet shake the couch; cushions compress and bounce
   rhythmically like a giant speaker at a rock concert; chains rattle and pull taut against walls;
   dust and tiny yellow padding fragments fall from the ceiling; overhead lamp swings; yellow spotlight pulses.
2) Brief pause — he pants, building tension.
3) Resume bouncing struggle on the cushions with erratic camera shake.
4) Sudden full stop — he centers, squints, and glares directly into the camera.
5) One explosive double-foot kick toward the lens; chains stretch; comic impact flash; couch rebounds once
   with exaggerated comic-book impact lines; hold angry glare to end.

Keep all objects structurally consistent with the input frame. English audio optional: only ambient room
rattle and muffled thuds, no speech.
"""


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    _load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print(
            "Missing GEMINI_API_KEY (or GOOGLE_API_KEY). Add a paid Gemini API key to this Cloud Agent's secrets.",
            file=sys.stderr,
        )
        return 2

    image_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_IMAGE
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT
    if not image_path.is_file():
        print(f"Image not found: {image_path}", file=sys.stderr)
        return 2

    client = genai.Client(api_key=api_key)
    image = types.Image.from_file(location=str(image_path))

    operation = client.models.generate_videos(
        model="veo-3.1-fast-generate-preview",
        prompt=MOTION_PROMPT.strip(),
        image=image,
        config=types.GenerateVideosConfig(
            resolution="720p",
            duration_seconds=8,
            negative_prompt="morphing into different character, redesigned logo, new text, subtitles, dialogue, realistic 3D, live action",
        ),
    )

    print("Veo generation started; polling…")
    while not operation.done:
        time.sleep(15)
        operation = client.operations.get(operation)
        print("  …still generating")

    if not operation.response or not operation.response.generated_videos:
        print(f"Generation failed: {operation}", file=sys.stderr)
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    video = operation.response.generated_videos[0]
    client.files.download(file=video.video, destination=str(out_path))
    print(f"Saved {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
