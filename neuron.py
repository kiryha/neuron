from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Mount the 'dist' folder created by the Docker build stage
app.mount("/", StaticFiles(directory="dist", html=True), name="static")

@app.get("/api/status")
async def status():
    return {"status": "Neuron Engine Online"}