# PROMPT: Implementation of "Neuron" - Latent Scene Engine

## Context & Vision
I am a 3D artist and pipeline developer building "Neuron," a next-generation VFX ecosystem. We are moving away from traditional Cartesian scene composition toward a coordinate-aligned latent space. Our first milestone is the "Material Hero"—a prompt-directed Implicit Neural Representation (INR) that can be iteratively refined and eventually animated via temporal models like Veo 3.1.

## High-Level Tech Stack
- **Backend**: FastAPI (Python 3.10), PyTorch, CLIP (for text conditioning).
- **Frontend**: React, Three.js, React-Three-Fiber, Drei (for OrbitControls/Grid).
- **Infrastructure**: Dockerized deployment on Hugging Face Spaces (Port 7860).
- **Data Source**: Synthetic renders and `transforms.json` exported from SideFX Houdini.

## Project Structure (The "Neuron" Package)
You must implement the following modular structure:
neuron_project/
├── neuron.py                # Entry point (FastAPI)
├── Dockerfile               # Multi-stage build (Node + Python)
├── neuron/                  # Logic Package
│   ├── api/routes.py        # /render and /status endpoints
│   ├── data/loader.py       # Houdini transforms.json parser
│   ├── models/inr.py        # MLP architecture for Material Hero
│   ├── rendering/raymarcher.py # Ray-marching & sampling logic
│   └── scene/graph.py       # Compositional Scene Graph logic (Phase 4)
└── src/                     # React/Three.js Frontend

## Implementation Plan (Step-by-Step)

### Step 1: Data Ingestion & Loader
- Implement `neuron/data/loader.py` to parse Houdini `transforms.json`.
- Map camera matrices to ray origins and directions.
- Prepare a PyTorch Dataset that pairs (x,y,z,view_dir) with RGB values from renders.

### Step 2: The Neural Engine (INR)
- Create a coordinate-based MLP in `neuron/models/inr.py`.
- Use Positional Encoding (Fourier features) for high-frequency detail.
- Implement text-conditioning: Use CLIP to embed material prompts (e.g., "Gold", "Velvet") as a global latent vector fed into the MLP.

### Step 3: Neural Rendering Pipeline
- Implement a `render_ray` function in `neuron/rendering/raymarcher.py`.
- The backend must accept a View Matrix from the frontend, march rays through the INR, and return a rendered frame (base64).

### Step 4: UI Development (Liquid Glass Aesthetic)
- Design a minimalistic, full-screen viewport.
- Create floating "Glassmorphism" widgets (frosted glass, sharp micro-borders).
- **Required Controls**:
    - **Prompt Bar**: Top-center, for material descriptions.
    - **Camera HUD**: Top-right, showing Focal Length and coordinates.
    - **Performance Panel**: Inference time (ms) and Resolution Scale toggle.
    - **Mode Toggle**: Switch between "Proxy" (standard Three.js wireframe) and "Neural" (the AI render).

### Step 5: Interaction Logic
- Use `OrbitControls`. Implement "Proxy-to-Neural" handoff:
    - During camera movement: Show a lightweight wireframe proxy at 60fps.
    - On movement stop: Trigger the backend `/render` call to "resolve" the neural pixels.

## Development Phases (For Reference)
1. Houdini Synthetic Data -> 2. Material Hero (INR) -> 3. Voxel Baking -> 4. Compositional Scene Graph -> 5. Production UI -> 6. Temporal Synthesis (Veo/LTX).

## Instructions for Cursor:
1. Analyze the existing `neuron.py` and `Dockerfile` in the root.
2. Build the `neuron/` folder structure as defined above.
3. Replace the "cyan sphere" in `App.jsx` with a dynamic viewport that pings the backend.
4. Provide a detailed summary of the code changes and any new dependencies needed in `requirements.txt`.