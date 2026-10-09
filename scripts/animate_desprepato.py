#!/usr/bin/env python3
"""Procedural 1980s heavy-metal comic-book animation from a single keyframe."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

SRC = Path("/home/ubuntu/.cursor/projects/workspace/assets/9241a1f2-4b81-44b3-a3d4-48641fcbd48c.jpg")
OUT = Path("/opt/cursor/artifacts/total_desprepato_animation.mp4")
FRAMES_DIR = Path("/tmp/desprepato_frames")
FPS = 24
DURATION_S = 10.0
W, H = 1024, 1024  # output size (crop center from source if needed)


@dataclass
class DustParticle:
    x: float
    y: float
    vx: float
    vy: float
    size: float
    alpha: float


def load_base() -> Image.Image:
    img = Image.open(SRC).convert("RGB")
    # Center-crop to square then resize for consistent output
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    return img.resize((W, H), Image.Resampling.LANCZOS)


def shake_offset(t: float, intensity: float, beat_hz: float = 2.5) -> tuple[float, float, float]:
    """Rhythmic comic shake: translation + slight rotation (degrees)."""
    phase = t * beat_hz * 2 * math.pi
    # Layered frequencies for chaotic metal feel
    dx = intensity * (
        math.sin(phase * 1.0) * 18
        + math.sin(phase * 2.3 + 0.7) * 9
        + math.sin(phase * 5.1) * 4
    )
    dy = intensity * (
        math.cos(phase * 1.1 + 0.2) * 16
        + math.cos(phase * 2.7) * 8
        + math.sin(phase * 4.4) * 3
    )
    rot = intensity * (math.sin(phase * 0.9) * 1.2 + math.sin(phase * 3.3) * 0.6)
    return dx, dy, rot


def apply_transform(base: Image.Image, dx: float, dy: float, rot_deg: float, scale: float = 1.0) -> Image.Image:
    cx, cy = W / 2, H / 2
    # Scale via resize then paste centered
    if scale != 1.0:
        nw, nh = int(W * scale), int(H * scale)
        scaled = base.resize((nw, nh), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (W, H), (20, 18, 12))
        ox = (W - nw) // 2 + int(dx)
        oy = (H - nh) // 2 + int(dy)
        canvas.paste(scaled, (ox, oy))
        base = canvas
        dx, dy = 0, 0
    return base.transform(
        (W, H),
        Image.Transform.AFFINE,
        (
            math.cos(math.radians(rot_deg)),
            -math.sin(math.radians(rot_deg)),
            dx + cx - cx * math.cos(math.radians(rot_deg)) + cy * math.sin(math.radians(rot_deg)),
            math.sin(math.radians(rot_deg)),
            math.cos(math.radians(rot_deg)),
            dy + cy - cx * math.sin(math.radians(rot_deg)) - cy * math.cos(math.radians(rot_deg)),
        ),
        resample=Image.Resampling.BICUBIC,
        fillcolor=(18, 16, 10),
    )


def pulse_light(img: Image.Image, t: float, intensity: float) -> Image.Image:
    beat = 0.5 + 0.5 * math.sin(t * 2.5 * 2 * math.pi)
    lamp_swing_x = 55 * math.sin(t * 1.8) + 18 * math.sin(t * 3.7 + 0.4)
    factor = 1.0 + intensity * (0.28 * beat + 0.1)
    arr = np.array(img, dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    # Overhead lamp hotspot swings
    lx, ly = W * 0.5 + lamp_swing_x, H * 0.12
    dist = np.sqrt((xx - lx) ** 2 + (yy - ly) ** 2)
    spot = np.clip(1.0 - dist / (W * 0.55), 0, 1) ** 2
    pulse = 1.0 + intensity * spot * (0.35 * beat + 0.15)
    arr *= factor
    arr[:, :, 0] *= 1.0 + spot * 0.06 * intensity
    arr[:, :, 1] *= 1.0 + spot * 0.12 * intensity
    arr[:, :, 2] *= 1.0 - spot * 0.04 * intensity
    arr *= pulse[:, :, np.newaxis]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def draw_speed_lines(draw: ImageDraw.ImageDraw, intensity: float, frame_i: int) -> None:
    if intensity < 0.25:
        return
    rng = random.Random(frame_i * 104729)
    cx, cy = W // 2, int(H * 0.62)
    for _ in range(int(10 + 30 * intensity)):
        angle = rng.uniform(0, 2 * math.pi)
        r0 = rng.randint(40, 120)
        r1 = r0 + rng.randint(60, int(140 + 80 * intensity))
        x0 = cx + r0 * math.cos(angle)
        y0 = cy + r0 * math.sin(angle)
        x1 = cx + r1 * math.cos(angle)
        y1 = cy + r1 * math.sin(angle)
        draw.line((x0, y0, x1, y1), fill=(15, 12, 8), width=rng.randint(2, 5))


def draw_vibration_lines(draw: ImageDraw.ImageDraw, intensity: float, frame_i: int) -> None:
    if intensity < 0.15:
        return
    n = int(12 + intensity * 36)
    rng = random.Random(frame_i * 7919)
    for _ in range(n):
        edge = rng.randint(0, 3)
        length = rng.randint(15, int(40 + 80 * intensity))
        thick = rng.randint(2, 4)
        if edge == 0:  # top
            x1, y1 = rng.randint(0, W), rng.randint(0, 40)
            x2, y2 = x1 + rng.randint(-20, 20), y1 + length
        elif edge == 1:  # bottom
            x1, y1 = rng.randint(0, W), rng.randint(H - 40, H)
            x2, y2 = x1 + rng.randint(-20, 20), y1 - length
        elif edge == 2:  # left
            x1, y1 = rng.randint(0, 40), rng.randint(0, H)
            x2, y2 = x1 + length, y1 + rng.randint(-20, 20)
        else:
            x1, y1 = rng.randint(W - 40, W), rng.randint(0, H)
            x2, y2 = x1 - length, y1 + rng.randint(-20, 20)
        draw.line((x1, y1, x2, y2), fill=(0, 0, 0), width=thick)


def draw_chain_rattle_lines(draw: ImageDraw.ImageDraw, t: float, intensity: float) -> None:
    if intensity < 0.2:
        return
    j = 6 * math.sin(t * 18) * intensity
    # Right wall chain zone (approx from keyframe)
    for i in range(5):
        x = int(W * 0.78 + j + i * 3)
        y0 = int(H * 0.35 + i * 45)
        draw.line((x, y0, x + int(8 * intensity), y0 + 25), fill=(40, 35, 30), width=3)
    for i in range(4):
        x = int(W * 0.22 - j - i * 2)
        y0 = int(H * 0.42 + i * 38)
        draw.line((x, y0, x - int(6 * intensity), y0 + 20), fill=(40, 35, 30), width=2)


def draw_impact_flash(overlay: Image.Image, strength: float) -> Image.Image:
    if strength <= 0:
        return overlay
    flash = Image.new("RGBA", (W, H), (255, 250, 220, int(255 * strength)))
    return Image.alpha_composite(overlay.convert("RGBA"), flash)


def draw_impact_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int) -> None:
    points = []
    for i in range(12):
        angle = i * math.pi / 6
        r = size if i % 2 == 0 else size // 2
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(points, outline=(0, 0, 0), fill=(255, 240, 120), width=4)
    for a in range(0, 360, 45):
        rad = math.radians(a)
        draw.line(
            (cx, cy, cx + size * 1.4 * math.cos(rad), cy + size * 1.4 * math.sin(rad)),
            fill=(0, 0, 0),
            width=5,
        )


def update_dust(particles: list[DustParticle], intensity: float) -> None:
    if intensity > 0.1 and random.random() < 0.35 * intensity:
        particles.append(
            DustParticle(
                x=random.uniform(W * 0.2, W * 0.8),
                y=random.uniform(0, H * 0.15),
                vx=random.uniform(-1.5, 1.5),
                vy=random.uniform(1.5, 4.5),
                size=random.uniform(1.5, 4.5),
                alpha=random.uniform(0.35, 0.85),
            )
        )
    alive: list[DustParticle] = []
    for p in particles:
        p.x += p.vx + random.uniform(-0.5, 0.5) * intensity
        p.y += p.vy
        p.alpha *= 0.985
        if p.y < H and p.alpha > 0.05:
            alive.append(p)
    particles[:] = alive[-120:]


def draw_dust(overlay: Image.Image, particles: list[DustParticle]) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for p in particles:
        c = int(180 * p.alpha)
        d.ellipse((p.x - p.size, p.y - p.size, p.x + p.size, p.y + p.size), fill=(c, c - 20, c - 40, c))
    return Image.alpha_composite(overlay.convert("RGBA"), layer)


def phase_envelope(t: float) -> tuple[float, str]:
    """Returns (motion_intensity 0-1, phase_name)."""
    if t < 6.5:
        return 1.0, "rampage"
    if t < 7.0:
        # Hard stop
        return 0.0, "freeze"
    if t < 7.35:
        return 0.05, "glare"
    if t < 7.55:
        return 1.35, "kick"
    if t < 8.2:
        # Single exaggerated bounce decay
        return 0.55 * math.exp(-(t - 7.55) * 6), "bounce"
    return 0.0, "hold"


def render_frame(base: Image.Image, t: float, frame_i: int, particles: list[DustParticle]) -> Image.Image:
    intensity, phase = phase_envelope(t)

    vertical_bounce = 0.0
    scale = 1.0
    if phase == "rampage":
        beat = math.sin(t * 2.5 * 2 * math.pi)
        vertical_bounce = beat * 14 * intensity
    elif phase == "kick":
        vertical_bounce = -22
        scale = 1.04
    elif phase == "bounce":
        vertical_bounce = math.sin((t - 7.55) * 28) * 14 * intensity

    dx, dy, rot = shake_offset(t, intensity)
    dy += vertical_bounce

    if phase == "glare":
        dx, dy, rot = 0, 0, 0
        scale = 1.08

    frame = apply_transform(base, dx, dy, rot, scale=scale)
    frame = pulse_light(frame, t, max(intensity, 0.08 if phase == "freeze" else 0))

    if phase == "glare":
        frame = ImageEnhance.Contrast(frame).enhance(1.12)
        frame = ImageEnhance.Sharpness(frame).enhance(1.15)

    overlay = frame.convert("RGBA")
    draw = ImageDraw.Draw(overlay)
    draw_vibration_lines(draw, intensity if phase not in ("freeze", "glare") else 0, frame_i)
    draw_speed_lines(draw, intensity if phase == "rampage" else 0, frame_i)
    draw_chain_rattle_lines(draw, t, intensity)

    if phase == "kick":
        draw_impact_star(draw, W // 2, int(H * 0.72), 85)
        overlay = draw_impact_flash(overlay, 0.55)
    elif phase == "bounce" and frame_i % 3 == 0:
        overlay = draw_impact_flash(overlay, 0.12 * intensity)

    update_dust(particles, intensity if phase == "rampage" else 0.05)
    overlay = draw_dust(overlay, particles)

    # Subtle vignette pulse
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    margin = int(30 + 25 * (1 - intensity))
    vd.rectangle((margin, margin, W - margin, H - margin), outline=(0, 0, 0, int(40 + 80 * intensity)), width=6)

    out = Image.alpha_composite(overlay, vig).convert("RGB")
    if intensity > 0.5 and phase == "rampage" and frame_i % 2 == 0:
        out = out.filter(ImageFilter.SHARPEN)
    return out


def main() -> None:
    random.seed(42)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    base = load_base()
    total_frames = int(DURATION_S * FPS)
    particles: list[DustParticle] = []

    for i in range(total_frames):
        t = i / FPS
        frame = render_frame(base, t, i, particles)
        frame.save(FRAMES_DIR / f"frame_{i:05d}.png")

    import subprocess

    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(FPS),
        "-i",
        str(FRAMES_DIR / "frame_%05d.png"),
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
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Wrote {OUT} ({total_frames} frames @ {FPS}fps)")


if __name__ == "__main__":
    main()
