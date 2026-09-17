# Material Hero application specification

Status: **Material Hero v0 fixed-view inference implemented and verified**

Last reviewed: 2026-09-17

## Objective

Provide a small web application where a user enters a supported material prompt and receives directly generated RGB from Three.js-rasterized surface context. The exported Sculpted Rubber Toy at the training-camera reference pose is the v0 reference case; orbit, zoom, and alternate supplied meshes are intentionally exposed as out-of-distribution experiments.

## Current implementation

- Frontend: React 18, Three.js, React Three Fiber, Drei, Vite
- Backend: FastAPI
- Deployment target: Docker-based Hugging Face Space on port `7860`
- Current viewport: one generated Material Hero result with orbit controls on a grid-free black background
- Web geometry: `public/geometry/material_hero/sculpted-rubber-toy.glb`, a verified 12,253,276-byte binary glTF exported from Houdini
- Active camera asset: `public/cameras/material_hero/cam_001.json`, copied unchanged from the selected dataset camera folder
- Geometry capture: square 1024 x 1024 float target used on demand for raw world-space `P`, smooth world-space `N`, normalized world-space `V`, and antialiased Coverage
- UI: `Reset Camera`, a compact prompt field, format guidance, and Render action; no pass-mode selector
- Current API: `/api/status` and `/api/render`
- Model: packaged `train/outputs/material-hero-v0-final/material_hero_v0.pt`, step 18,100

## Implemented local normal viewer

Before prompt or model integration, the placeholder sphere was replaced with a local-only Three.js normal-pass viewer:

- load `public/geometry/material_hero/sculpted-rubber-toy.glb`;
- render the GLB's smooth normals explicitly in world space;
- calculate raw world-space position `P`, smooth world-space normal `N`, and normalized world-space view direction `V = normalize(cameraPosition - P)`;
- retain the selected pass as floating-point components for later model input;
- preview all three passes as RGB using `display = value * 0.5 + 0.5`, without changing the raw offscreen values;
- use a grid-free black display background;
- keep the camera orbitable;
- load the dataset camera's position, target, up vector, focal length, horizontal aperture, and resolution from `cam_001.json`;
- derive the Three.js vertical field of view from the horizontal aperture, focal length, and render aspect ratio;
- provide a reset control that restores this dataset camera pose and projection;
- use world origin `[0, 0, 0]` as the OrbitControls target because all Houdini dataset cameras aim at origin;
- use the camera JSON resolution for the internal normal render target, independent of the responsive display size.

The reference view is loaded from the copied dataset camera JSON. The hero GLB remains at its exported identity transform; the application does not recenter or rescale it. No geometry metadata file or formal pixel-precise validation gate is required. The implementation explicitly outputs world-space normals rather than relying on a generic visualization material with an implicit coordinate convention.

The prompt uses the controlled `base [optional color] finish condition` structure. The explicit aliases `dirty → dusty` and `gray → grey` are accepted. Submitting captures all geometry inputs at the current camera, calls FastAPI, and displays the returned RGBA PNG. During orbit, the stale result is hidden and a live normal preview keeps navigation responsive; OrbitControls `end` automatically requests a new generated result. Reset restores `cam_001` and regenerates the supported reference view.

The backend loads the packaged checkpoint strictly, preserves its stored `P` normalization, normalizes `N` and `V`, and predicts linear foreground RGB only for covered pixels. It converts linear RGB to sRGB for the PNG and stores Coverage as alpha. Model retraining, arbitrary language, novel-view support, alternate geometry support, and Hugging Face deployment remain deferred.

Verified on 2026-09-03:

- the GLB loads without console or runtime errors;
- the viewport displays the world-space normal visualization rather than shaded material output;
- orbiting updates the visible surface continuously;
- reset restores the same reference camera position, target, and field of view;
- the internal normal target remains 1024 x 1024 as the browser window changes;
- `npm run build` completes successfully.

Verified on 2026-09-04:

- the app loads `cam_001.json` and uses it for the initial and reset camera;
- the Three.js vertical field of view is derived from the dataset lens and aperture rather than hard-coded;
- the normal target uses the JSON resolution and aspect ratio;
- the GLB is rendered at its exported identity transform without application-side centering;
- the UI exposes one persistent generated-result mode; raw float32 `P`, `N`, `V`, and Coverage remain internal model inputs;
- `npm run build` completes successfully with both the camera JSON and GLB in the production output.
- Render and camera-release events update the packaged model result from raw float32 `P`, `N`, `V`, and Coverage;
- orbiting hides the stale generated image, shows responsive geometry feedback, and automatically replaces it after inference completes;
- a live browser run completed `gold polished clean` inference through the CUDA backend and displayed the RGBA result;
- `/api/status` reports model step 18,100, CUDA device, and the fixed `sculpted_rubber_toy/cam_001` scope.

## Dataset camera matching

Datarender writes one `{dataset}/{geometry_id}/{camera_id}/{camera_id}.json` containing the cooked Houdini camera's world position, forward-derived target, up vector, focal length, horizontal aperture, and render resolution. Copy the selected record unchanged to `public/cameras/material_hero/{camera_id}.json` and use it to initialize the Three.js training-camera reference view. The active dataset v0 camera is `public/cameras/material_hero/cam_001.json`. Its `target` records a point along the camera's forward axis, not the interaction pivot. All Houdini dataset cameras aim at world origin, so Three.js uses `[0, 0, 0]` as the orbit and reset look-at target.

Camera data is necessary but not sufficient for matching the model inputs. The web implementation must also keep the hero GLB's position, rotation, scale, and centering consistent with Houdini; use the JSON resolution's aspect ratio; reproduce the world-space and unit conventions of `P`; reproduce the world-axis convention of smooth unbumped `N`; and calculate normalized `V` from the surface toward the camera. For the first fixed-view experiment, keep the centered hero at an identity transform in both applications rather than adding a geometry metadata file.

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
- hide the stale neural frame while a new result is pending and show the live normal preview;
- identify the training-camera reference pose;
- label other views and meshes as out of distribution for the loaded checkpoint;
- show clear loading, unsupported-prompt, and inference-error states.

The current implementation follows this pattern: the normal visualization updates while the user orbits, and inference starts when OrbitControls reports the interaction has ended.

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
