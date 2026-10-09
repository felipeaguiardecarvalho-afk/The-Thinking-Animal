#!/usr/bin/env python3
"""Build a comic motion video from keyframe stills (crossfade + impact effects)."""

from __future__ import annotations

import math
import random
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

BASE = Path("/home/ubuntu/.cursor/projects/workspace/assets/9241a1f2-4b81-44b3-a3d4-48641fcbd48c.jpg")
FRAMES = [
    Path("/opt/cursor/artifacts/assets/desprepato_kf_thrash.jpg"),
    Path("/opt/cursor/artifacts/assets/desprepato_kf_bounce.jpg"),
    Path("/opt/cursor/artifacts/assets/desprepato_kf_glare.jpg"),
    Path("/opt/cursor/artifacts/assets/desprepato_kf_kick.jpg"),
]
OUT = Path("/opt/cursor/artifacts/total_desprepato_animation.mp4")
TMP = Path("/tmp/desprepato_kf_seq")
FPS = 24
SIZE = 1024


def load(path: Path) -> Image.Image:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    return img.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def ease(t: float) -> float:
    return t * t * (3 - 2 * t)


def blend(a: Image.Image, b: Image.Image, t: float) -> Image.Image:
    t = ease(max(0.0, min(1.0, t)))
    return Image.blend(a, b, t)


def shake(img: Image.Image, intensity: float, seed: int) -> Image.Image:
    if intensity <= 0:
        return img
    rng = random.Random(seed)
    dx = int(rng.uniform(-1, 1) * 10 * intensity)
    dy = int(rng.uniform(-1, 1) * 10 * intensity)
    rot = rng.uniform(-1, 1) * 1.2 * intensity
    return img.transform(
        (SIZE, SIZE),
        Image.Transform.AFFINE,
        (
            math.cos(math.radians(rot)),
            -math.sin(math.radians(rot)),
            dx,
            math.sin(math.radians(rot)),
            math.cos(math.radians(rot)),
            dy,
        ),
        resample=Image.Resampling.BICUBIC,
        fillcolor=(18, 16, 10),
    )


def pulse_light(img: Image.Image, beat: float, swing: float) -> Image.Image:
    arr = np.array(img, dtype=np.float32)
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    lx, ly = SIZE * 0.5 + swing, SIZE * 0.12
    dist = np.sqrt((xx - lx) ** 2 + (yy - ly) ** 2)
    spot = np.clip(1.0 - dist / (SIZE * 0.55), 0, 1) ** 2
    mult = 1.0 + 0.25 * beat * spot
    arr *= mult[:, :, np.newaxis]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def overlay_fx(img: Image.Image, intensity: float, frame_i: int, flash: float = 0) -> Image.Image:
    layer = img.convert("RGBA")
    draw = ImageDraw.Draw(layer)
    if intensity > 0.2:
        rng = random.Random(frame_i * 9973)
        for _ in range(int(6 + 20 * intensity)):
            x1 = rng.randint(0, SIZE)
            y1 = rng.choice([rng.randint(0, 40), rng.randint(SIZE - 40, SIZE)])
            draw.line((x1, y1, x1 + rng.randint(-15, 15), y1 + rng.randint(20, 60)), fill=(0, 0, 0, 180), width=3)
        for _ in range(int(4 * intensity)):
            x = rng.uniform(SIZE * 0.2, SIZE * 0.8)
            y = rng.uniform(0, SIZE * 0.2)
            r = rng.uniform(1, 3)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(160, 150, 120, 200))
    if flash > 0:
        flash_layer = Image.new("RGBA", (SIZE, SIZE), (255, 245, 200, int(255 * flash)))
        layer = Image.alpha_composite(layer, flash_layer)
    return layer.convert("RGB")


def hold(frames: list[Image.Image], img: Image.Image, n: int, *, intensity: float, start_i: int) -> int:
    beat_phase = start_i / FPS
    for i in range(n):
        beat = 0.5 + 0.5 * math.sin(beat_phase * 5)
        swing = 20 * math.sin(beat_phase * 2.2) * intensity
        f = shake(img, intensity * 0.15, start_i + i)
        f = pulse_light(f, beat * intensity, swing)
        f = overlay_fx(f, intensity, start_i + i)
        frames.append(f)
        beat_phase += 1 / FPS
    return start_i + n


def transition(
    frames: list[Image.Image], a: Image.Image, b: Image.Image, n: int, *, intensity: float, start_i: int
) -> int:
    beat_phase = start_i / FPS
    for i in range(n):
        t = (i + 1) / n
        f = blend(a, b, t)
        beat = 0.5 + 0.5 * math.sin(beat_phase * 6)
        swing = 25 * math.sin(beat_phase * 2.5) * intensity
        f = shake(f, intensity, start_i + i)
        f = pulse_light(f, beat * intensity, swing)
        flash = 0.35 if t > 0.85 and intensity > 0.8 else 0
        f = overlay_fx(f, intensity, start_i + i, flash=flash)
        frames.append(f)
        beat_phase += 1 / FPS
    return start_i + n


def main() -> None:
    random.seed(7)
    base = load(BASE)
    kf = [load(p) for p in FRAMES]
    thrash, bounce, glare, kick = kf

    timeline: list[tuple[str, ...]] = [
        ("hold", base, 20, 0.05),
        ("trans", base, thrash, 44, 1.0),
        ("hold", thrash, 10, 0.35),
        ("trans", thrash, bounce, 36, 0.95),
        ("trans", bounce, thrash, 32, 0.9),
        ("trans", thrash, glare, 28, 0.4),
        ("hold", glare, 22, 0.0),
        ("trans", glare, kick, 14, 0.5),
        ("hold", kick, 10, 0.25),
        ("trans", kick, glare, 20, 0.35),
        ("hold", glare, 24, 0.0),
    ]

    frames: list[Image.Image] = []
    idx = 0
    for step in timeline:
        kind = step[0]
        if kind == "hold":
            _, img, n, inten = step
            idx = hold(frames, img, n, intensity=inten, start_i=idx)
        else:
            _, a, b, n, inten = step
            idx = transition(frames, a, b, n, intensity=inten, start_i=idx)

    TMP.mkdir(parents=True, exist_ok=True)
    for i, fr in enumerate(frames):
        fr.save(TMP / f"frame_{i:05d}.png")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(FPS),
        "-i",
        str(TMP / "frame_%05d.png"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "18",
        "-movflags",
        "+faststart",
        str(OUT),
    ]
    subprocess.run(cmd, check=True)
    print(f"Wrote {OUT} ({len(frames)} frames, {len(frames)/FPS:.2f}s)")


if __name__ == "__main__":
    main()
