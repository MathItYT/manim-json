from manim.camera.camera import Camera
import numpy as np


def manim_to_pixel(
    points: np.ndarray,
    camera: Camera
) -> np.ndarray:
    """Convert manim coordinates to pixel coordinates.

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
    points[:, 0] = (points[:, 0] - camera.frame_center[0])
    points[:, 1] = (points[:, 1] - camera.frame_center[1])
    points[:, 0] += camera.frame_width / 2
    points[:, 1] -= camera.frame_height / 2
    points[:, 1] *= -1
    points *= camera.pixel_height / camera.frame_height
    return points
