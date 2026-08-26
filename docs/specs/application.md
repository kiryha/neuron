# Material Hero application specification

Status: **Scaffold only**

Last reviewed: 2026-08-26

## Objective

Provide a small web application where a user enters a supported material prompt, controls the camera around the fixed Sculpted Rubber Toy, and receives the model’s directly generated RGB appearance.

## Current implementation

- Frontend: React 18, Three.js, React Three Fiber, Drei, Vite
- Backend: FastAPI
- Deployment target: Docker-based Hugging Face Space on port `7860`
- Current viewport: cyan emissive sphere with orbit controls and grid
- Current API: `/api/status`
- Training/model inference: not implemented

## Intended user flow

1. The application loads the model and fixed Material Hero proxy.
2. The user enters a compact prompt such as `gold brushed dirty`.
3. The application validates or normalizes the prompt against the supported vocabulary.
4. The viewport supplies camera state and fixed geometry context.
5. The backend or client inference path generates final RGB.
6. The generated image is displayed from the requested camera.
7. Camera or prompt changes request a new image while preserving hero identity.

## Display behavior

The first application may use the explicit hero geometry as a proxy for navigation and silhouette generation. The neural model supplies final pixels; it does not create a Three.js PBR material.

A practical interaction pattern is:

- show a lightweight proxy while the camera is moving;
- request or evaluate neural output when movement pauses;
- keep the last valid neural frame visible while a new result is pending;
- show clear loading, unsupported-prompt, and inference-error states.

Exact real-time behavior depends on measured inference performance and remains open.

## Prompt behavior

- Support the material vocabulary represented in the training release.
- Accept normalized combinations of base, optional color, finish, and condition.
- Map explicit aliases such as `dirty` to canonical terms where documented.
- Do not imply support for arbitrary objects or scenes.
- Show the normalized prompt and unsupported tokens when validation fails.

The first version is deterministic. Repeating the same prompt and camera against the same model version should reproduce the same output.

## Logical render request

The final transport is not frozen, but a render request must logically contain:

```json
{
  "prompt": "gold brushed dirty",
  "camera": {
    "camera_to_world": [[0, 0, 0, 0]],
    "intrinsics": [[0, 0, 0], [0, 0, 0], [0, 0, 1]]
  },
  "width": 512,
  "height": 512,
  "model_version": "material-hero-v1"
}
```

The matrices above illustrate required structure only. Their real conventions must match the dataset specification.

## Logical render response

- Generated RGB image or a stable URL/byte response for that image
- Normalized prompt
- Model version
- Render/inference duration
- Request ID
- Structured error when generation fails

Do not return invented shader parameters or material maps.

## Model package requirements

The deployed model artifact should include:

- weights;
- architecture/configuration;
- prompt vocabulary and aliases;
- normalization constants and positional encoding settings;
- fixed geometry/proxy reference and hash;
- camera convention;
- expected color space and output transform;
- dataset release/version;
- representative validation renders.

This package can later inform the first `.neuron` asset format, but a general neural-asset standard is outside the current milestone.

## API and deployment requirements

- `/api/status` reports whether a model is loaded and its version.
- A render endpoint validates request shape and prompt vocabulary.
- Startup fails clearly when required weights or configuration are absent.
- Docker build includes the frontend and Python runtime needed for inference.
- Hugging Face deployment uses external model storage/LFS when weights should not live in normal Git history.
- Local and deployed behavior use the same model configuration.

## Acceptance criteria

- A clean build serves the frontend and backend.
- The app loads one documented Material Hero checkpoint.
- Supported prompts produce visibly different, appropriate appearances.
- The same prompt and camera are reproducible.
- Camera changes preserve the fixed hero identity.
- Unsupported prompts fail clearly or normalize through documented aliases.
- The UI never claims to generate arbitrary geometry, maps, or relighting.

## Non-goals

- General-purpose text-to-image generation
- Arbitrary geometry generation
- Shader or texture export
- Scene assembly
- Character animation
- Full USD or neural-asset management
