"""Houdini UI for Material Hero dataset rendering."""

import json
import math
import shutil
from pathlib import Path

import hou
from PySide6 import QtCore, QtWidgets

from datagen import config
from datagen.ui import ui_datarender


CAMERA_APERTURE_MM = 20.955
STAGE_PATH = "/stage"
CAMERA_DOME_PATH = "/stage/camera_dome"
NEUROMAT_PATH = "/stage/neuromat"
RENDER_SETTINGS_PATH = "/stage/karmarendersettings"
RENDER_ROP_PATH = "/stage/usdrender_rop1"


def _camera_positions(camera_count, distance):
    """Return evenly distributed positions on a full sphere."""

    golden_angle = math.pi * (3.0 - math.sqrt(5.0))
    positions = []

    for index in range(camera_count):
        y = 1.0 - 2.0 * (index + 0.5) / camera_count
        ring_radius = math.sqrt(1.0 - y * y)
        angle = index * golden_angle
        positions.append(
            (
                math.cos(angle) * ring_radius * distance,
                y * distance,
                math.sin(angle) * ring_radius * distance,
            )
        )

    return positions


def create_camera_dome(camera_count, focal_length, object_size, frame_margin):
    """Create a Solaris camera-dome subnet."""

    stage = hou.node(STAGE_PATH)
    if stage is None:
        raise RuntimeError(f"Network not found: {STAGE_PATH}")

    camera_dome = stage.createNode("subnet", "camera_dome")

    half_fov = math.atan(CAMERA_APERTURE_MM / (2.0 * focal_length))
    distance = object_size * 0.5 / math.sin(half_fov) * frame_margin
    previous = camera_dome.indirectInputs()[0]

    for index, position in enumerate(_camera_positions(camera_count, distance)):
        camera_name = f"cam_{index:03d}"
        camera = camera_dome.createNode("camera", camera_name)
        camera.setInput(0, previous)
        camera.parm("primpath").set(f"/cameras/{camera_name}")
        camera.parmTuple("t").set(position)
        camera.parm("lookatenable").set(1)
        camera.parmTuple("lookatposition").set((0.0, 0.0, 0.0))
        camera.parm("focalLength_control").set("set")
        camera.parm("focalLength").set(focal_length)
        camera.parm("horizontalAperture_control").set("set")
        camera.parm("horizontalAperture").set(CAMERA_APERTURE_MM)
        previous = camera

    output = camera_dome.node("output0")
    output.setInput(0, previous)
    output.setDisplayFlag(True)

    camera_dome.moveToGoodPosition()
    camera_dome.layoutChildren()

    return camera_dome, distance


def _camera_list(single_camera, single_camera_name):
    """Return camera IDs and USD primitive paths for this render."""

    if single_camera:
        camera_name = single_camera_name.strip()
        if not camera_name:
            raise RuntimeError("Single camera name is empty.")
        return [(camera_name, f"/cameras/{camera_name}")]

    camera_dome = hou.node(CAMERA_DOME_PATH)
    if camera_dome is None:
        raise RuntimeError(f"Node not found: {CAMERA_DOME_PATH}")

    cameras = []
    for node in camera_dome.children():
        if node.type().name() == "camera":
            cameras.append((node.name(), node.evalParm("primpath")))

    if not cameras:
        raise RuntimeError(f"No cameras found in {CAMERA_DOME_PATH}")

    return sorted(cameras)


def render_dataset(
    dataset_root,
    dataset_name,
    geometry_name,
    cameras,
    material_json,
):
    """Set the selected material library on neuromat and render every record."""

    neuromat = hou.node(NEUROMAT_PATH)
    render_settings = hou.node(RENDER_SETTINGS_PATH)
    render_rop = hou.node(RENDER_ROP_PATH)

    for node_path, node in (
        (NEUROMAT_PATH, neuromat),
        (RENDER_SETTINGS_PATH, render_settings),
        (RENDER_ROP_PATH, render_rop),
    ):
        if node is None:
            raise RuntimeError(f"Node not found: {node_path}")

    material_json = Path(material_json).resolve()
    if not material_json.is_file():
        raise RuntimeError(f"Material JSON not found: {material_json}")

    neuromat.parm("dataset_path").set(str(material_json))

    with material_json.open("r", encoding="utf-8") as file:
        materials = json.load(file)

    if not materials:
        raise RuntimeError(f"Material JSON is empty: {material_json}")

    dataset_dir = Path(dataset_root).expanduser() / dataset_name
    dataset_dir.mkdir(parents=True, exist_ok=True)

    json_snapshot = dataset_dir / material_json.name
    if not json_snapshot.exists():
        shutil.copy2(material_json, json_snapshot)

    frame = hou.intFrame()
    material_ids = sorted(materials)
    total_items = len(cameras) * len(material_ids)
    pending_items = []
    skipped = 0

    for camera_name, camera_path in cameras:
        for material_id in material_ids:
            material_dir = dataset_dir / geometry_name / camera_name / material_id
            if material_dir.exists():
                skipped += 1
            else:
                pending_items.append(
                    (camera_name, camera_path, material_id, material_dir)
                )

    rendered = 0
    completed_items = skipped

    print("Dataset Render Started...")
    if skipped:
        print(f"RESUME {skipped}/{total_items} existing renders")

    with hou.InterruptableOperation(
        "Dataset Render",
        open_interrupt_dialog=True,
    ) as progress:
        progress.updateProgress(completed_items / total_items)

        for camera_name, camera_path, material_id, material_dir in pending_items:
            item_name = f"{camera_name}/{material_id}"

            render_settings.parm("camera").set(camera_path)
            material_dir.mkdir(parents=True)
            output_path = material_dir / "render.exr"

            neuromat.parm("material_id").set(material_id)
            render_settings.parm("picture").set(output_path.as_posix())

            print(f"RENDER {item_name}")
            render_rop.render(frame_range=(frame, frame))
            rendered += 1
            completed_items += 1
            progress.updateProgress(completed_items / total_items)

    print("Dataset Render Complete!")
    return rendered, skipped


class Datarender(QtWidgets.QDialog, ui_datarender.Ui_Datarender):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        self.boxJSONName.addItems(config.LIBRARY_JSONS)
        self.btnCameraDome.clicked.connect(self.create_camera_dome)
        self.btnRenderDataset.clicked.connect(self.render_dataset)

    def create_camera_dome(self):
        try:
            camera_count = int(self.linNumCameras.text())
            focal_length = float(self.linFocalLen.text())
            object_size = float(self.linObjectSize.text())
            frame_margin = float(self.linMargin.text())

            if (
                camera_count < 1
                or focal_length <= 0
                or object_size <= 0
                or frame_margin < 1.0
            ):
                raise ValueError

            camera_dome, distance = create_camera_dome(
                camera_count,
                focal_length,
                object_size,
                frame_margin,
            )
        except ValueError:
            hou.ui.displayMessage(
                "Camera count, focal length, and object size must be positive. "
                "Frame margin must be 1.0 or greater.",
                severity=hou.severityType.Error,
            )
            return
        except RuntimeError as error:
            hou.ui.displayMessage(
                str(error),
                severity=hou.severityType.Error,
            )
            return

        hou.ui.displayMessage(
            f"Created {camera_count} cameras in {camera_dome.path()}.\n"
            f"Camera distance: {distance:.3f} m",
        )

    def render_dataset(self):
        try:
            dataset_root = self.linDatasetRoot.text().strip()
            dataset_name = self.linDatasetName.text().strip()
            geometry_name = self.linSingleGeometryName.text().strip()

            if not dataset_root or not dataset_name or not geometry_name:
                raise RuntimeError(
                    "Dataset root, dataset name, and geometry name are required."
                )

            cameras = _camera_list(
                self.chbSingleCamera_2.isChecked(),
                self.linSingleCameraName.text(),
            )
            material_json = config.LIBRARY_JSONS[self.boxJSONName.currentText()]
            rendered, skipped = render_dataset(
                dataset_root,
                dataset_name,
                geometry_name,
                cameras,
                material_json,
            )
        except hou.OperationInterrupted:
            print("Dataset Render Interrupted!")
            hou.ui.displayMessage(
                "Dataset render interrupted.\n"
                "The last RENDER folder may be incomplete; inspect or delete it "
                "before resuming.",
            )
            return
        except (RuntimeError, OSError, json.JSONDecodeError, hou.Error) as error:
            hou.ui.displayMessage(
                str(error),
                severity=hou.severityType.Error,
            )
            return

        hou.ui.displayMessage(
            f"Dataset render finished.\nRendered: {rendered}\nSkipped: {skipped}",
        )


def run_datarender():
    datarender = Datarender()
    datarender.show()
