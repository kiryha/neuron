# Neuron: Latent Scene Engine

Neuron is an experimental 3D application architecture designed to bridge the gap between traditional VFX pipelines and generative world models. It replaces explicit geometric data (vertices, normals, textures) with a Neural Voxel Field (NVF) and Implicit Neural Representations (INR), allowing for high-fidelity scene generation that remains spatially consistent and artistically controllable.

## Project Concept

In a traditional pipeline, scenes are composed of discrete assets and lights within a Cartesian coordinate system. In Neuron, the scene exists as a coordinate-aligned latent space.

Instead of manual sculpting and shading, artists use prompt-directed entities. By leveraging semantic-local latent spaces, Neuron allows for non-destructive, iterative refinement. A prompt change such as adding "rain" or "wear and tear" modifies the high-frequency details of the neural field without destabilizing the underlying spatial structure or camera orientation.

The ultimate architectural goal of Neuron is to move beyond monolithic scene generation toward a modular, production-ready Digital Content Creation (DCC) ecosystem:

### Modular Neural Assets
Assets such as characters, environments, and props are treated as independent "Latent Fragments." These are stored as discrete neural weight files (.neuron) rather than static meshes. This allows for a referencing system similar to USD, where assets can be loaded, versioned, and updated across multiple shots without redundant data overhead.

### Compositional Neural Scene Graphs (CNSG)
Neuron implements a Compositional Neural Scene Graph to manage complex shots. By placing "Neural Proxies" in the viewport, the engine performs real-time coordinate transformations. When a camera ray intersects a proxy, the system transforms the ray into the asset's local latent space, allowing multiple independent neural fields to coexist and interact within a single global environment.

### Neural Deformation and Animation
Animation in Neuron shifts from vertex-based rigging to learned "Deformation Fields." Characters are defined in a canonical neural state, and animation is achieved by warping the coordinate space based on pose-vectors (e.g., joint rotations). This allows for complex secondary effects like muscle bulge and skin sliding to emerge naturally from the neural representation rather than being manually simulated.

### Production Pipeline Integration
While Neuron functions as a standalone generative engine, it is designed to bridge into established VFX workflows. The final goal includes modules for "baking" these dynamic latent scenes into 3D Gaussian Splatting (3DGS) stages or high-density USD assets, ensuring that the creative flexibility of AI is backed by the reliability of industry-standard delivery formats.

## Architecture

Neuron is designed as a web-based application hosted on Hugging Face Spaces, utilizing a client-server model to separate 3D manipulation from neural inference.

### 1. Frontend (The Viewport)
- Framework: React with Three.js / React Three Fiber.
- Functionality: Provides a standard 3D viewport with camera controls (Orbit/Fly) and scene hierarchy. It manages the camera transform matrix and proxy geometry (greyboxes).
- Interaction: The viewport sends camera coordinates and prompt strings to the backend to receive a neural-rendered frame.

### 2. Backend (The Neural Engine)
- Framework: Python (PyTorch) with FastAPI or Gradio.
- Inference: A coordinate-based MLP (Multi-Layer Perceptron) or Transformer that samples the latent field.
- Logic: For every ray-marched point (x, y, z) and text embedding (w), the model returns color (RGB) and density (sigma).

### 3. Data and Training
- Synthetic Data: Trained on high-quality multi-view datasets generated procedurally in SideFX Houdini.
- Storage: Model weights and latent embeddings are managed via Hugging Face LFS.
- Conditioning: Uses CLIP or similar encoders to map natural language prompts to vectors that steer the neural field's output.

## Technical Implementation

Neuron utilizes a hybrid approach to ensure production-grade stability:

- Neural Voxel Fields (NVF): A sparse voxel grid provides spatial anchoring, ensuring that objects do not "drift" or "shimmer" when the camera moves.
- Implicit Neural Representation (INR): Sub-voxel details are generated on-the-fly, allowing for infinite resolution and complex material behavior (refraction, caustics) without the overhead of heavy meshes.
- Latent Anchoring: Global structural features are locked to specific latent seeds, while descriptive prompts perturb only the relevant semantic layers of the model.

## Development Roadmap

- Phase 1: Implementation of a hardcoded "Hello World" scene (Cornell Box) with interactive camera controls.
- Phase 2: Integration of multi-resolution hash grids for increased rendering performance on home-grade hardware.
- Phase 3: Development of the "Material Library" logic, allowing prompt-based swapping of surfaces on fixed geometry.
- Phase 4: Implementation of USD and 3D Gaussian Splat export modules for integration with Maya and Houdini.

## Usage

To run the application locally or on a private Hugging Face Space:

1. Clone the repository with Git LFS support.
2. Install Python dependencies: pip install -r requirements.txt.
3. Launch the server: python app.py.
4. Access the web interface via the provided local or cloud URL.

## Hugging Face
Clone the Repo:
```
git lfs install
git clone https://huggingface.co/spaces/YourUsername/Neuron
```

Setup Local Dev:
```
pip install -r requirements.txt
npm install # for the frontend
```