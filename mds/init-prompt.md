# PROMPT: Implementation of "Neuron" - Latent Scene Engine

## Context & Vision
I am a 3D artist and pipeline developer building "Neuron," a next-generation VFX ecosystem. We are moving away from traditional Cartesian scene composition toward a coordinate-aligned latent space. Our first milestone is the "Material Hero"—a prompt-directed Implicit Neural Representation (INR) that can be iteratively refined and eventually animated via temporal models like Veo 3.1. Check README.md for more details.

## Coding Style
Keep amount of code at absolute minimum, do not over-complicate. Use descriptive variable and function names. 
Add high level comments that descrybe more WHY we doing this, instead of WHAT, (what we do can be grasped from code), be smart with comments, they should add to the code, not duplicate.

## High-Level Tech Stack
- **Backend**: FastAPI (Python 3.10), PyTorch, CLIP (for text conditioning).
- **Frontend**: React, Three.js, React-Three-Fiber, Drei (for OrbitControls/Grid).
- **Infrastructure**: Dockerized deployment on Hugging Face Spaces (Port 7860).
- **Data Source**: Synthetic renders and `transforms.json` exported from SideFX Houdini.

## Project Structure (The "Neuron" Package)

You should organize the repo as follows:

- **neuron.py** &nbsp;&nbsp;&nbsp;&nbsp;→ Entry point (FastAPI backend)
- **Dockerfile** &nbsp;&nbsp;&nbsp;&nbsp;→ Multi-stage build (Node + Python)
- **neuron/** &nbsp;&nbsp;&nbsp;&nbsp;→ Main backend logic package  
    - **api/routes.py** &nbsp;&nbsp;&nbsp;&nbsp;→ Implements `/render` and `/status` endpoints  
    - **data/loader.py** &nbsp;&nbsp;&nbsp;&nbsp;→ Houdini `transforms.json` parser  
    - **models/inr.py** &nbsp;&nbsp;&nbsp;&nbsp;→ MLP architecture for the "Material Hero"  
    - **rendering/raymarcher.py** &nbsp;&nbsp;&nbsp;&nbsp;→ Ray-marching and sampling logic  
    - **scene/graph.py** &nbsp;&nbsp;&nbsp;&nbsp;→ Compositional Scene Graph (for modular assets, Phase 4)
- **src/** &nbsp;&nbsp;&nbsp;&nbsp;→ React/Three.js frontend

(Use plain bullets/indentation for compatibility with GitHub markdown. Add code comments in each file describing its high-level purpose.)

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

### Step 6: Training Utility (`train/train_hero.py`)
- Create a standalone training script using PyTorch.
- **Memory Management**: Implement "Gradient Accumulation" and "Mixed Precision" to support training on a 6GB VRAM GPU.
- **Masking**: Include logic to ignore the bottom-right corner of training images (Houdini Apprentice watermark).
- **Checkpointing**: Automatically save the model state (`.pth` file) to `train/outputs/` every 500 iterations.
- **Validation**: Every 1000 steps, render a single low-res test view to track visual progress.

## Development Phases (For Reference)
1. Houdini Synthetic Data -> 2. Material Hero (INR) -> 3. Voxel Baking -> 4. Compositional Scene Graph -> 5. Production UI -> 6. Temporal Synthesis (Veo/LTX).

## Instructions for Cursor:
1. Analyze the existing `neuron.py` and `Dockerfile` in the root.
2. Build the `neuron/` folder structure as defined above.
3. Replace the "cyan sphere" in `App.jsx` with a dynamic viewport that pings the backend.
4. Provide a detailed summary of the code changes and any new dependencies needed in `requirements.txt`.