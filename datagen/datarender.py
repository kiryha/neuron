"""Houdini UI for Material Hero dataset rendering."""

import math

import hou
from PySide6 import QtCore, QtWidgets

from datagen.ui import ui_datarender


CAMERA_APERTURE_MM = 20.955
FRAME_MARGIN = 1.1
STAGE_PATH = "/stage"


def _camera_positions(camera_count, distance):
    """Return evenly distributed positions on an upper hemisphere."""

    golden_angle = math.pi * (3.0 - math.sqrt(5.0))
    positions = []

    for index in range(camera_count):
        y = (index + 0.5) / camera_count
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


def create_camera_dome(camera_count, focal_length, object_size):
    """Create a Solaris camera-dome subnet."""

    stage = hou.node(STAGE_PATH)
    if stage is None:
        raise RuntimeError(f"Network not found: {STAGE_PATH}")

    camera_dome = stage.createNode("subnet", "camera_dome")

    half_fov = math.atan(CAMERA_APERTURE_MM / (2.0 * focal_length))
    distance = object_size * 0.5 / math.sin(half_fov) * FRAME_MARGIN
    previous = camera_dome.indirectInputs()[0]

    for index, position in enumerate(_camera_positions(camera_count, distance)):
        camera_name = f"cam_{index:04d}"
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


class Datarender(QtWidgets.QDialog, ui_datarender.Ui_Datarender):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        self.btnCameraDome.clicked.connect(self.create_camera_dome)

    def create_camera_dome(self):
        try:
            camera_count = int(self.linNumCameras.text())
            focal_length = float(self.linFocalLen.text())
            object_size = float(self.linObjectSize.text())

            if camera_count < 1 or focal_length <= 0 or object_size <= 0:
                raise ValueError

            camera_dome, distance = create_camera_dome(
                camera_count,
                focal_length,
                object_size,
            )
        except ValueError:
            hou.ui.displayMessage(
                "Camera count, focal length, and object size must be positive numbers.",
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


def run_datarender():
    datarender = Datarender()
    datarender.show()
