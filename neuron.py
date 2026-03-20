from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Dummy endpoint for the future Neural Renderer
@app.get("/api/status")
async def status():
    return {"status": "Neuron Engine Offline - Waiting for Model"}

# Serve the React build files
app.mount("/", StaticFiles(directory="dist", html=True), name="static")

@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    return FileResponse("dist/index.html")