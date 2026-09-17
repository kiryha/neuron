from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from neuron.inference import MaterialHeroInference, PromptError


ROOT = Path(__file__).resolve().parent
CHECKPOINT = ROOT / "train" / "outputs" / "material-hero-v0-final" / "material_hero_v0.pt"
MAX_PIXELS = 1024 * 1024

engine = MaterialHeroInference(CHECKPOINT)
app = FastAPI()


@app.get("/api/status")
async def status():
    return {
        "status": "ready",
        "model": "material_hero_v0",
        "checkpoint_step": engine.step,
        "device": str(engine.device),
        "scope": "sculpted_rubber_toy/cam_001",
    }


async def read_float_buffer(upload: UploadFile, expected_values: int) -> np.ndarray:
    content = await upload.read()
    if len(content) != expected_values * 4:
        raise HTTPException(status_code=422, detail=f"{upload.filename} has the wrong size.")
    return np.frombuffer(content, dtype="<f4").copy()


@app.post("/api/render")
async def render(
    prompt: str = Form(...),
    width: int = Form(...),
    height: int = Form(...),
    position: UploadFile = File(...),
    normal: UploadFile = File(...),
    view: UploadFile = File(...),
    coverage: UploadFile = File(...),
):
    if width <= 0 or height <= 0 or width * height > MAX_PIXELS:
        raise HTTPException(status_code=422, detail="Resolution exceeds the v0 limit.")
    pixels = width * height
    try:
        png, normalized_prompt = engine.render_png(
            prompt,
            (await read_float_buffer(position, pixels * 3)).reshape(pixels, 3),
            (await read_float_buffer(normal, pixels * 3)).reshape(pixels, 3),
            (await read_float_buffer(view, pixels * 3)).reshape(pixels, 3),
            await read_float_buffer(coverage, pixels),
            width,
            height,
        )
    except PromptError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return Response(
        content=png,
        media_type="image/png",
        headers={"X-Normalized-Prompt": normalized_prompt},
    )


app.mount("/", StaticFiles(directory=ROOT / "dist", html=True), name="static")


@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    return FileResponse(ROOT / "dist" / "index.html")
