# Connect Gemini (Cloud Agent + local Cursor)

## 1. API key for video generation (Veo)

This repo uses the **Gemini API** via `scripts/generate_desprepato_veo.py`.

1. Create a key: [Google AI Studio → API keys](https://aistudio.google.com/apikey)
2. In **Cursor → Cloud Agents → your environment → Secrets**, add:
   - Name: `GEMINI_API_KEY`
   - Value: your `AIza...` key (paid tier required for Veo)
3. **Start a new agent run** on this repo so the secret is injected.

Verify in the agent:

```bash
test -n "$GEMINI_API_KEY" && echo ok
python3 scripts/generate_desprepato_veo.py
```

`GOOGLE_API_KEY` is also accepted if you prefer that name.

## 2. Gemini Docs MCP (optional, no key)

Project config: `.cursor/mcp.json` points at Google's public **Gemini Docs MCP** (`gemini_search_docs`, `gemini_get_doc`).

- **Desktop:** reload MCP under Settings → Features → MCP after pulling this file.
- **Cloud Agent:** add the same server in your environment's MCP settings if you want docs tools in the cloud VM.

This does **not** replace `GEMINI_API_KEY` for generating videos.

## 3. Alternative: SnapGen

If Gemini credits are exhausted, use SnapGen with `SNAPGEN_API_KEY` and their video API or MCP (`https://api.snapgen.org/mcp`). See [SnapGen MCP docs](https://docs.snapgen.org/integrations/mcp).
