from manim.mobject.types.vectorized_mobject import VMobject
from manim.mobject.mobject import Mobject
from manim.mobject.types.image_mobject import ImageMobject
from manim.mobject.types.point_cloud_mobject import PMobject
from manim.camera.camera import Camera
from manim.camera.three_d_camera import ThreeDCamera
from manim.utils.family import extract_mobject_family_members
from manim_json.manim_to_pixel import manim_to_pixel
from typing import Any


def update_json(
    mobjects: list[Mobject],
    frame: int, 
    json: dict[int, dict[str, Any]],
    camera: Camera
) -> None:
    """Update the json[frame] dictionary with the mobjects' properties.

    Parameters
    ----------
    mobjects : list[Union[VMobject, ImageMobject]]
        The mobjects to update the json dictionary with.
    frame : int
        The frame number.
    json : dict[str, dict[str, Any]]
        The json dictionary to update.
    """
    json[frame] = {}
    if isinstance(camera, ThreeDCamera):
        raise NotImplementedError("3D camera not supported yet")
    for mobject in extract_mobject_family_members(mobjects, only_those_with_points=True):
        if isinstance(mobject, VMobject):
            mobject_id: str = str(id(mobject))
            json[frame][mobject_id] = {}
            json[frame][mobject_id]["type"] = VMobject.__name__
            json[frame][mobject_id]["fill_color"] = str(mobject.fill_color or mobject.color)
            json[frame][mobject_id]["fill_opacity"] = mobject.get_fill_opacity()
            json[frame][mobject_id]["stroke_color"] = str(mobject.stroke_color or mobject.color)
            json[frame][mobject_id]["stroke_opacity"] = mobject.get_stroke_opacity()
            json[frame][mobject_id]["stroke_width"] = mobject.stroke_width / 100 * camera.pixel_width / camera.frame_width
            json[frame][mobject_id]["points"] = manim_to_pixel(mobject.points[:,:2], camera).tolist()
        elif isinstance(mobject, ImageMobject):
            mobject_id: str = str(id(mobject))
            json[frame][mobject_id] = {}
            json[frame][mobject_id]["type"] = ImageMobject.__name__
            json[frame][mobject_id]["pixel_array"] = mobject.pixel_array.tolist()
            json[frame][mobject_id]["points"] = manim_to_pixel(mobject.points[:,:2], camera).tolist()
        elif isinstance(mobject, PMobject):
            mobject_id: str = str(id(mobject))
            json[frame][mobject_id] = {}
            json[frame][mobject_id]["type"] = PMobject.__name__
            json[frame][mobject_id]["color"] = str(mobject.color)
            json[frame][mobject_id]["stroke_width"] = mobject.stroke_width / 100 * camera.pixel_width / camera.frame_width
            json[frame][mobject_id]["points"] = manim_to_pixel(mobject.points[:,:2], camera).tolist()
        elif isinstance(mobject, Mobject):
            continue
        else:
            raise TypeError(f"Unsupported mobject type: {type(mobject)}")
