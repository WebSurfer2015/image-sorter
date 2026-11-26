import base64
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import APIError, OpenAI
import uvicorn

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

app = FastAPI(title="Local AI Image Assistant")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
PORT = int(os.getenv("PORT", "8000"))


@app.get("/")
async def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.post("/api/analyze")
async def analyze_image(image: UploadFile = File(...)):
    token = os.getenv("AI_BUILDER_TOKEN")
    if not token:
        raise HTTPException(503, "AI_BUILDER_TOKEN is missing. Add it to the local .env file and restart the app.")
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(415, "Please upload an image file.")
    data = await image.read(12 * 1024 * 1024 + 1)
    if len(data) > 12 * 1024 * 1024:
        raise HTTPException(413, "Image must be 12 MB or smaller.")
    if not data:
        raise HTTPException(400, "The uploaded image is empty.")

    data_url = f"data:{image.content_type};base64,{base64.b64encode(data).decode('ascii')}"
    client = OpenAI(base_url="https://space.ai-builders.com/backend/v1", api_key=token)
    prompt = """Analyze this image for a personal photo and document organizer. Return only a JSON object with exactly these keys:
category (short category), summary (clear concise sentence describing visible content),
tags (array of 3-8 concise strings), suggested_filename (safe descriptive filename including a suitable extension).
Use the original file extension if it is available; otherwise infer a suitable one. Do not claim uncertain details as facts."""
    try:
        response = client.chat.completions.create(
            model="gemini-3.8-flash",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}},
            ]}],
            response_format={"type": "json_object"},
            max_tokens=700,
        )
        content = response.choices[0].message.content
        result = json.loads(content or "{}")
    except (APIError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(502, f"Image analysis failed: {type(exc).__name__}") from exc

    required = ("category", "summary", "tags", "suggested_filename")
    if any(key not in result for key in required) or not isinstance(result["tags"], list):
        raise HTTPException(502, "The model returned an incomplete analysis. Please try again.")
    name = re.sub(r"[^\w. -]", "", str(result["suggested_filename"])).strip(" .")[:100]
    result["suggested_filename"] = name or "image"
    result["tags"] = [str(tag)[:50] for tag in result["tags"][:12]]
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
