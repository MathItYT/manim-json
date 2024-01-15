from manim.scene.scene import Scene
from manim.mobject.mobject import Mobject
from manim.mobject.types.vectorized_mobject import VMobject
from manim.mobject.types.image_mobject import ImageMobject
from manim.mobject.types.point_cloud_mobject import PMobject
from manim_json.pixel_to_manim import pixel_to_manim
from typing import Any, Union
import numpy as np
import json


class JSONScene(Scene):
    """A scene that can be constructed from a JSON file."""
    json_data: Union[str, dict[str, dict[str, Any]]]

    def construct(self):
        if isinstance(self.json_data, str):
            with open(self.json_data, "r") as f:
                self.data = json.load(f)
        else:
            self.data = self.json_data
        self.mobjects_from_data = {}
        for frame in self.data.values():
            for i, obj in frame.items():
                mob = self.from_json(i, obj)
                self.add(mob)
            self.wait(1 / self.camera.frame_rate)
            self.clear()
    
    def from_json(self, i: str, obj: dict[str, Any]) -> Mobject:
        """Construct a Mobject from a JSON object.

        Parameters
        ----------
        obj : dict[str, str]
            The JSON object to construct from.

        Returns
        -------
        Mobject
            The constructed Mobject.
        """
        if obj["type"] == "VMobject":
            return self.from_json_vmobject(i, obj)
        elif obj["type"] == "ImageMobject":
            return self.from_json_imagemobject(i, obj)
        elif obj["type"] == "PMobject":
            return self.from_json_pmobject(i, obj)
        else:
            raise ValueError(f"Unknown type: {obj['type']}")
    
    def from_json_vmobject(self, i: int, obj: dict[str, Any]) -> VMobject:
        """Construct a VMobject from a JSON object.

        Parameters
        ----------
        obj : dict[str, str]
            The JSON object to construct from.

        Returns
        -------
        VMobject
            The constructed VMobject.
        """
        mob = self.mobjects_from_data.get(i)
        if mob is None:
            mob = VMobject()
            self.mobjects_from_data[i] = mob
        mob.set_points(pixel_to_manim(np.array(obj["points"]), self.camera))
        mob.set_fill(obj["fill_color"], obj["fill_opacity"], False)
        mob.set_stroke(
            obj["stroke_color"],
            self.handle_stroke_width(obj["stroke_width"]),
            obj["stroke_opacity"],
            family=False
        )
        return mob

    def from_json_imagemobject(self, i: int, obj: dict[str, Any]) -> ImageMobject:
        """Construct an ImageMobject from a JSON object.

        Parameters
        ----------
        obj : dict[str, str]
            The JSON object to construct from.

        Returns
        -------
        ImageMobject
            The constructed ImageMobject.
        """
        mob = self.mobjects_from_data.get(i)
        if mob is None:
            mob = ImageMobject(obj["pixel_array"])
            self.mobjects_from_data[i] = mob
        mob.points = pixel_to_manim(np.array(obj["points"]), self.camera)
        return mob

    def from_json_pmobject(self, i: int, obj: dict[str, Any]) -> PMobject:
        """Construct a PMobject from a JSON object.

        Parameters
        ----------
        obj : dict[str, str]
            The JSON object to construct from.

        Returns
        -------
        PMobject
            The constructed PMobject.
        """
        mob = self.mobjects_from_data.get(i)
        if mob is None:
            mob = PMobject()
            self.mobjects_from_data[i] = mob
        mob.add_points(pixel_to_manim(np.array(obj["points"]), self.camera))
        mob.set_color(obj["color"], family=False)
        mob.set_stroke_width(self.handle_stroke_width(obj["stroke_width"]), family=False)
        return mob
    
    def handle_stroke_width(self, stroke_width: float) -> float:
        """Handle the stroke width.

        Parameters
        ----------
        stroke_width : float
            The stroke width to handle.

        Returns
        -------
        float
            The handled stroke width.
        """
        return stroke_width * self.camera.frame_width / self.camera.pixel_width * 100
