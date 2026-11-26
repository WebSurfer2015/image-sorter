# AI Image Sorter

A small FastAPI app for analyzing personal photos and documents with Gemini 3.8 Flash.

## Run locally

1. Copy `.env.example` to `.env` and set `AI_BUILDER_TOKEN` in `.env`.
2. Run `uv sync`.
3. Run `uv run uvicorn app:app --host 127.0.0.1 --port 8000`.
4. Open <http://127.0.0.1:8000>.

The browser talks only to this app's backend. The backend sends the uploaded image to AI Builders Space for model analysis. Do not put API keys in browser code or commit `.env`.

## Deploy

The repository includes a Dockerfile that honors the platform-provided `PORT`. Before deploying, update `deploy-config.json` with the actual public GitHub repository URL. Keep `AI_BUILDER_TOKEN` out of `env_vars`; AI Builders Space injects it at runtime. The first deployment binds a service name permanently to its repository URL.
