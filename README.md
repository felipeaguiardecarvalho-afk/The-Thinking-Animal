# The-Thinking-Animal

## Total Desprepato animation

Real motion (character thrashing, bouncing cushions, rattling chains) requires **image-to-video** (e.g. Gemini **Veo 3.1**), not a shaking still frame.

### Generate without Gemini credits (default in this repo)

Uses Cursor **GenerateImage** keyframes + crossfade compositing:

```bash
pip install -r requirements-animation.txt
python3 scripts/compose_keyframe_video.py
```

Keyframes live under `/opt/cursor/artifacts/assets/desprepato_kf_*.jpg`. Regenerate them with `GenerateImage` if you change the motion brief.

Output: `/opt/cursor/artifacts/total_desprepato_animation.mp4`

### Optional: Veo (when Gemini credits available)

```bash
export GEMINI_API_KEY=...
python3 scripts/generate_desprepato_veo.py
```

### Deprecated

`scripts/animate_desprepato.py` — single-image shake only; do not use.
