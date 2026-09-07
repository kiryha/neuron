"""Command-line entry point for rendering a dataset without Houdini's GUI."""

import argparse
import json
import sys
from pathlib import Path

import hou


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from datagen.datarender import render_dataset  # noqa: E402


def _arguments():
    parser = argparse.ArgumentParser(
        description="Load a Houdini scene and render a Material Hero dataset."
    )
    parser.add_argument("--scene", required=True, help="Houdini .hiplc scene")
    parser.add_argument("--material-json", required=True, help="DEV or PROD JSON")
    parser.add_argument("--dataset-root", required=True)
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--geometry", required=True, help="Dataset geometry ID")
    parser.add_argument("--camera", required=True, help="Camera ID, e.g. cam_001")
    return parser.parse_args()


def main():
    args = _arguments()
    scene_path = Path(args.scene).expanduser().resolve()
    material_json = Path(args.material_json).expanduser().resolve()

    if not scene_path.is_file():
        raise RuntimeError(f"Houdini scene not found: {scene_path}")
    if not material_json.is_file():
        raise RuntimeError(f"Material JSON not found: {material_json}")

    if scene_path.parent.name.lower() == "scenes":
        project_root = scene_path.parent.parent
    else:
        project_root = scene_path.parent
    hou.putenv("JOB", str(project_root))

    print(f"SCENE {scene_path}", flush=True)
    print(f"MATERIAL JSON {material_json}", flush=True)
    print("Loading Houdini scene without GUI...", flush=True)
    hou.hipFile.load(
        str(scene_path),
        suppress_save_prompt=True,
        ignore_load_warnings=True,
    )

    camera_name = args.camera.strip()
    if not camera_name:
        raise RuntimeError("Camera name is empty.")

    rendered, skipped = render_dataset(
        args.dataset_root,
        args.dataset_name,
        args.geometry,
        [(camera_name, f"/cameras/{camera_name}")],
        material_json,
    )
    print(f"Rendered: {rendered}", flush=True)
    print(f"Skipped: {skipped}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, hou.OperationInterrupted):
        print("Dataset Render Interrupted!", flush=True)
        print(
            "The last RENDER folder may be incomplete; inspect or delete it "
            "before resuming.",
            flush=True,
        )
        raise SystemExit(130)
    except (RuntimeError, OSError, json.JSONDecodeError, hou.Error) as error:
        print(f"ERROR: {error}", flush=True)
        raise SystemExit(1)
