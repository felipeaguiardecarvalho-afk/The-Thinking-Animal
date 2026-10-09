# The-Thinking-Animal

## Total Desprepato animation

Real motion (character thrashing, bouncing cushions, rattling chains) requires **image-to-video** (e.g. Gemini **Veo 3.1**), not a shaking still frame.

### Generate with Veo (recommended)

1. Add a paid [Gemini API key](https://aistudio.google.com/apikey) to this Cloud Agent as secret `GEMINI_API_KEY`.
2. Run:

```bash
pip install -r requirements-animation.txt
python3 scripts/generate_desprepato_veo.py
```

Output: `/opt/cursor/artifacts/total_desprepato_animation.mp4`

### Legacy fallback

`scripts/animate_desprepato.py` only composites camera shake on the keyframe — use Veo for the intended result.
