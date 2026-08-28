---
title: Neuron
emoji: 🧠
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Neuron
![Data Model](images/neuromat.jpg)

Neuron is a personal generative-AI research project built from the ground up to learn how text-conditioned image generation works. Its first milestone, **Material Hero**, generates the rendered appearance of one fixed 3D object from a material description.

Example prompts:

- `gold brushed dirty`
- `black rubber polished scratched`
- `clear glass clean`

The current focus is deliberately narrow: many materials, one geometry, controlled cameras, and controlled studio lighting. This makes it possible to study text conditioning, neural rendering, multi-view consistency, dataset design, and deployment without first solving general text-to-3D generation.

## Material Hero

Material Hero uses a **Sculpted Rubber Toy** as its single fixed geometry. Houdini procedurally renders that object with many combinations of material base, finish, condition, and color. Each rendered view is linked to a canonical text description and the camera and geometry data required for training.

The trained model will directly predict the final rendered RGB appearance. It will **not** generate PBR shader parameters or texture maps.

Conceptually, the first model learns:

```text
RGB = F(surface position, surface normal, view direction, text description)
```

The fixed geometry supplies the surface and silhouette; the prompt controls its appearance. As a result, every generation depicts the same Material Hero, while prompts change qualities such as material, color, finish, dirt, wear, and bump character.

### Initial constraints

- One fixed hero geometry
- Controlled material vocabulary
- Fixed studio lighting and color-management configuration
- Camera-conditioned, multi-view output
- Direct RGB generation
- Deterministic appearance for a given prompt in the first version
- No arbitrary object or scene generation
- No generated shader graphs, material parameters, or texture maps
- No user-controlled relighting in the first version

These are intentional scope boundaries, not final limitations of the wider Neuron concept.

## Pipeline

```text
Houdini procedural materials
        |
        v
Multi-view RGB images + prompts + camera/geometry metadata
        |
        v
Text-conditioned neural appearance model
        |
        v
Neuron web viewport on Hugging Face Spaces
```

### 1. Data generation

SideFX Houdini and Karma generate the synthetic ground-truth dataset. The current material system includes procedural variation, dirt, wear, and bump signals and is being completed and validated before batch rendering.

Each training record is expected to preserve at least:

- material ID and canonical prompt;
- camera ID, transform, and intrinsics;
- beauty RGB image and alpha;
- world-space position and surface normal data;
- the render configuration needed for reproducibility.

Additional AOVs are useful for diagnostics and possible auxiliary supervision, but RGB remains the generated result.

### 2. Training

The first training implementation will learn prompt-conditioned appearance on the fixed hero surface. All views of a material must remain in the same dataset split so validation measures generalization to unseen material combinations rather than memorization of alternate camera views.

The training implementation has not been built yet. It begins after the Houdini dataset and manifest have been validated.

### 3. Application

The intended application accepts a material prompt and displays the generated Material Hero from the active camera. The viewport camera supplies view information to the neural renderer.

The current React application is only a visual scaffold with a placeholder sphere. The FastAPI backend currently exposes a status endpoint and serves the built frontend; neural inference is not connected yet.

## Current status

The project is currently finishing **Phase 1: Houdini data generation**.

- The procedural material library and semantic label generator exist.
- A small stress-test material set is used to validate shader behavior.
- Variation, dirt, and wear systems are implemented in the Houdini material HDA.
- Stochastic, directional, and cellular bump branches are implemented; fixed-camera stress validation is the current Houdini work area.
- Dataset batching, final renders, training, and neural inference remain to be implemented.
- The browser UI and backend are scaffolds, not a functioning model demo.

Final dataset renders must also be produced without the watermark present in the current Houdini Apprentice development renders.

## Roadmap

### Phase 1 — Material dataset

- Finish and validate the Houdini material HDA.
- Confirm required RGB, alpha, geometry, camera, and metadata outputs.
- Render the material stress set.
- Automate and render the complete dataset.

### Phase 2 — Material Hero model

- Implement the dataset loader and validation tools.
- Establish a simple text-conditioned RGB baseline.
- Train for consistent appearance across camera views.
- Evaluate both seen materials and held-out material combinations.
- Save a reproducible model artifact with its vocabulary and configuration.

### Phase 3 — Neuron application

- Replace the placeholder sphere with the Material Hero viewport representation.
- Connect prompt and camera input to model inference.
- Display generated RGB results interactively.
- Package and deploy the application on Hugging Face Spaces.

### Later research — persistent neural assets

The longer-term Neuron direction is a 3D application built from versioned neural assets: promptable objects, characters, and environments that can be referenced and composed into shots through a USD-like scene graph.

Material Hero is intended to become the first small neural asset and to test the foundational ideas of persistent model state, prompt conditioning, camera-aware rendering, versioning, and viewport integration. General neural geometry, multi-asset composition, relighting, deformation, and animation are future research and are not part of the current Material Hero milestone.

## Repository structure

```text
datagen/       Material definitions and Houdini data-generation tools
train/         Training package scaffold
neuron/        Future neural-engine package
src/           React and React Three Fiber frontend
main.py        FastAPI application and static frontend server
docs/          Canonical project documentation
docs/sources/  Historical briefs, exported chats, and source material
```

Start with [docs/START-HERE.md](docs/START-HERE.md) for the current status, decisions, specifications, and runbooks.

Files in `docs/sources/` preserve project history and rationale. They may contain outdated or speculative advice and are not, by themselves, the current specification.

## Run the current scaffold

### Frontend development

```bash
npm ci
npm run dev
```

Vite serves the development frontend on port `5173`.

### Production-style local run

```bash
npm ci
npm run build
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 7860
```

This serves the built frontend and the placeholder FastAPI backend on port `7860`.

### Docker

The included `Dockerfile` builds the React frontend and serves it through FastAPI using the same port expected by Hugging Face Spaces.

## Hugging Face

The repository is configured for a Docker-based Hugging Face Space. Deployment is planned after the first trained Material Hero model is integrated.
