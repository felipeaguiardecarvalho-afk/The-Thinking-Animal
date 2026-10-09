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

### Connect Gemini (Veo)

1. Add Cloud Agent secret **`GEMINI_API_KEY`** ([AI Studio key](https://aistudio.google.com/apikey)).
2. Start a **new** agent run (secrets load at boot).
3. Run:

```bash
python3 scripts/generate_desprepato_veo.py
```

Details: [docs/GEMINI_SETUP.md](docs/GEMINI_SETUP.md). Optional **Gemini Docs MCP** is in `.cursor/mcp.json`.

### Deprecated

`scripts/animate_desprepato.py` — single-image shake only; do not use.
