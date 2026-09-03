# Material Hero application specification

Status: **Scaffold only; local normal-viewer slice specified**

Last reviewed: 2026-09-03

## Objective

Provide a small web application where a user enters a supported material prompt and receives directly generated RGB from Three.js-rasterized surface context. The exported Sculpted Rubber Toy at the training-camera reference pose is the v0 reference case; orbit, zoom, and alternate supplied meshes are intentionally exposed as out-of-distribution experiments.

## Current implementation

- Frontend: React 18, Three.js, React Three Fiber, Drei, Vite
- Backend: FastAPI
- Deployment target: Docker-based Hugging Face Space on port `7860`
- Current viewport: cyan emissive sphere with orbit controls and grid
- Web geometry: `public/models/material_hero/sculpted-rubber-toy.glb`, a verified 12,253,888-byte binary glTF exported from Houdini; it is present but not yet loaded by the viewport
- Current API: `/api/status`
- Training/model inference: not implemented

## Next implementation slice: local normal viewer

Before prompt or model integration, replace the placeholder sphere with a local-only Three.js normal-pass viewer:

- load `public/models/material_hero/sculpted-rubber-toy.glb`;
- render the GLB's smooth normals explicitly in world space;
- retain the normal data as floating-point components in `[-1, 1]` for later model input;
- display that data as RGB using `display = N * 0.5 + 0.5`;
- use a black display background;
- keep the camera orbitable;
- provide a reset control that restores a stable app-authored reference camera position, target, and field of view;
- use a square 1024 x 1024 internal normal render target, independent of the responsive display size.

The reference view is stored directly in application code. It does not require a geometry metadata file and is not a formal pixel-precise match to the Houdini training camera. The implementation must explicitly output world-space normals rather than relying on a generic visualization material with an implicit coordinate convention.

This slice runs through the local Vite development server. It does not include prompt input, generated RGB, model inference, `P`, `V`, or Coverage rendering, FastAPI changes, or Hugging Face deployment.

Acceptance for this slice:

- the GLB loads without console or runtime errors;
- the viewport displays the world-space normal visualization rather than shaded material output;
- orbiting updates the visible surface continuously;
- reset restores the same reference camera position, target, and field of view;
- the internal normal target remains 1024 x 1024 as the browser window changes;
- `npm run build` completes successfully.

## Intended user flow

1. The application loads the neural model and `sculpted-rubber-toy.glb`; additional test meshes may be added for out-of-distribution experiments.
2. The user enters a compact prompt such as `gold brushed dirty`.
3. The application validates or normalizes the prompt against the supported vocabulary.
4. Three.js rasterizes `P`, smooth unbumped `N`, and material-independent Coverage for the active supplied mesh and camera, then derives `V` from position and camera state. Its Coverage convention must match Houdini Beauty alpha (`C.A`).
5. The backend or client inference path generates final RGB.
6. The generated image is displayed from the requested camera.
7. Prompt, camera, or mesh changes request a new image; v0 results outside the training-camera reference pose are labeled experimental and may be broken.

## Display behavior

The application uses the single exported hero GLB to generate geometry buffers and display a responsive mesh preview. The neural model supplies final pixels; it does not create a Three.js PBR material. The first checkpoint is trained on only the Sculpted Rubber Toy at one camera, so the UI must not imply that orbit, zoom, or mesh switching is supported merely because an image is returned.

A practical interaction pattern is:

- show the Three.js mesh preview while the camera is moving;
- request or evaluate neural output when movement pauses;
- keep the last valid neural frame visible while a new result is pending;
- identify the training-camera reference pose;
- label other views and meshes as out of distribution for the loaded checkpoint;
- show clear loading, unsupported-prompt, and inference-error states.

Exact real-time behavior depends on measured inference performance and remains open.

For the local normal-viewer slice, the normal visualization updates continuously while the user orbits. Deferred neural-output behavior does not apply yet.

## Prompt behavior

- Support the material vocabulary represented in the training release.
- Accept normalized combinations of base, optional color, finish, and condition.
- Map explicit aliases such as `dirty` to canonical terms where documented.
- Do not imply support for arbitrary objects or scenes.
- Show the normalized prompt and unsupported tokens when validation fails.

The first version is deterministic. Repeating the same prompt and camera against the same model version should reproduce the same output.

## Logical render request

The final binary transport is not frozen, but a render request must logically contain:

```json
{
  "prompt": "gold brushed dirty",
  "geometry_id": "sculpted_rubber_toy",
  "geometry_buffers": {
    "position": "binary-reference",
    "normal": "binary-reference",
    "view_direction": "binary-reference",
    "coverage": "binary-reference"
  },
  "width": 512,
  "height": 512,
  "model_version": "material-hero-model-v0"
}
```

The buffer references above illustrate required structure only. The model receives `V` directly, so separate camera matrices are not required by the inference request. Large floating-point buffers should use an appropriate binary transport rather than JSON arrays. Their conventions must match the dataset specification.

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
- the web hero mesh path plus any compatible experimental test meshes;
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
- The same prompt, geometry buffers, and camera are reproducible.
- Three.js loads the exported hero GLB and produces `P`, smooth unbumped `N`, `V`, and Coverage at the training-camera reference pose; formal pixel-precise comparison against Houdini is not required for v0.
- Orbit, zoom, and alternate-mesh controls produce recordable results and clearly identify when the request is out of distribution.
- Unsupported prompts fail clearly or normalize through documented aliases.
- The UI never claims to generate arbitrary geometry, maps, or relighting.

## Non-goals

- General-purpose text-to-image generation
- Geometry generation
- Reliable arbitrary-view or arbitrary-geometry rendering from the v0 checkpoint
- Shader or texture export
- Scene assembly
- Character animation
- Full USD or neural-asset management
