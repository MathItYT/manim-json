import base64

import numpy as np

from manim._config import config
from manim.camera.camera import CapStyleType, LineJointType
from manim.mobject.mobject import Mobject
from manim.mobject.types.image_mobject import ImageMobject
from manim.mobject.types.point_cloud_mobject import PMobject
from manim.mobject.types.vectorized_mobject import VMobject
from manim.scene.scene import Scene
from manim.utils.family_ops import extract_mobject_family_members


class JSONCamera:
    """A camera that outputs its data to a JSON file instead of rendering it."""
    
    def __init__(self):
        self.background = config.background_color
        self.background_opacity = config.background_opacity
        self.pixel_width = config.pixel_width
        self.pixel_height = config.pixel_height
        self.frame_width = config.frame_width
        self.frame_height = config.frame_height
        self.frame_rate = config.frame_rate
        self.use_z_index = False
    
    def get_objects_data(self, scene: Scene) -> list[dict]:
        """Get the data for the objects in the scene."""
        objects_data = []
        for mobject in extract_mobject_family_members(scene.mobjects):
            object_data = self.get_object_data(mobject)
            if object_data is not None:
                objects_data.append(object_data)
        return objects_data

    def get_object_data(self, mobject: Mobject) -> dict | None:
        """Get the data for a single object."""
        if isinstance(mobject, VMobject):
            return self.get_vmobject_data(mobject)
        elif isinstance(mobject, ImageMobject):
            return self.get_image_mobject_data(mobject)
        elif isinstance(mobject, PMobject):
            return self.get_pmobject_data(mobject)
        return None

    def get_vmobject_data(self, mobject: VMobject) -> dict:
        """Get the data for a vectorized mobject."""
        if mobject.get_num_points() == 0:
            return None
        return {
            "type": "VMobject",
            "points": [point[:2] for point in mobject.points.tolist()],
            "fill": self.parse_rgbas(mobject.fill_rgbas),
            "stroke": self.parse_rgbas(mobject.stroke_rgbas),
            "gradient_points": self.parse_gradient_points(mobject.get_gradient_start_and_end_points()),
            "line_cap": self.parse_cap_style(mobject.cap_style),
            "line_join": self.parse_joint_type(mobject.joint_type),
            "stroke_width": mobject.get_stroke_width(),
            "background_stroke_width": mobject.get_stroke_width(background=True),
            "background_stroke": self.parse_rgbas(mobject.background_stroke_rgbas),
        }
    
    def parse_rgbas(self, rgbas: list[list[float]]) -> str:
        """Parse the fill color."""
        return list(map(lambda rgba: [rgba[0], rgba[1], rgba[2], rgba[3]], rgbas))

    def parse_gradient_points(self, gradient_points: tuple[np.ndarray, np.ndarray]) -> list[list[float]]:
        """Parse the gradient points."""
        return [point.tolist()[:2] for point in gradient_points]
    
    def parse_cap_style(self, cap_style: str) -> str:
        """Parse a cap style."""
        if cap_style == CapStyleType.ROUND:
            return "round"
        elif cap_style == CapStyleType.BUTT:
            return "butt"
        elif cap_style == CapStyleType.SQUARE:
            return "square"
        return "butt"
    
    def parse_joint_type(self, joint_type: str) -> str:
        """Parse a joint type."""
        if joint_type == LineJointType.ROUND:
            return "round"
        elif joint_type == LineJointType.BEVEL:
            return "bevel"
        elif joint_type == LineJointType.MITER:
            return "miter"
        return "miter"
    
    def get_image_mobject_data(self, mobject: ImageMobject) -> dict:
        """Get the data for an image mobject."""
        return {
            "type": "ImageMobject",
            "image_base64": base64.b64encode(mobject.pixel_array).decode("utf-8"),
            "height": mobject.height,
            "width": mobject.width,
            "top_left": mobject.points[0].tolist()
        }
    
    def get_pmobject_data(self, mobject: PMobject) -> dict:
        """Get the data for a point cloud mobject."""
        return {
            "type": "PMobject",
            "points": mobject.points.tolist(),
            "color": mobject.color,
            "gradient_points": mobject,
            "line_cap": mobject.cap_style,
            "line_join": mobject.joint_type,
            "stroke_width": mobject.get_stroke_width(),
            "background_stroke_width": mobject.get_stroke_width(background=True)
        }
