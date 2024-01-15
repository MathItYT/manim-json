from manim.camera.camera import Camera
import numpy as np


def pixel_to_manim(points: np.ndarray, camera: Camera) -> np.ndarray:
    """Convert pixel coordinates to manim coordinates.

    Parameters
    ----------
    points : np.ndarray
        The points to convert.
    camera : Camera
        The camera to use.

    Returns
    -------
    np.ndarray
        The converted points.
    """
    points = points.copy()
    if len(points) == 0:
        return points
    points[:, 0] *= camera.frame_height / camera.pixel_height
    points[:, 1] *= camera.frame_height / camera.pixel_height
    points[:, 1] *= -1
    points[:, 1] += camera.frame_height / 2
    points[:, 0] -= camera.frame_width / 2
    points[:, 1] += camera.frame_center[1]
    points[:, 0] += camera.frame_center[0]
    points = np.append(points, np.zeros((len(points), 1)), axis=1)
    return points
