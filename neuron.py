import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from neuron.api.routes import router as api_router

app = FastAPI(title="Neuron Latent Engine")

# Include modularized routes
app.include_router(api_router, prefix="/api")

# Serve Frontend
app.mount("/", StaticFiles(directory="dist", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("neuron:app", host="0.0.0.0", port=7860, reload=True)