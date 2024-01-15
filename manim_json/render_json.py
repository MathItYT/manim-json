from manim.scene.scene import Scene
from manim_json.update_json import update_json
import json


def render_json(scene: Scene, file_name: str):
    json_dict = {}
    scene.add_updater(lambda dt: update_json(
        scene.mobjects,
        round(scene.renderer.time * scene.camera.frame_rate),
        json_dict,
        scene.camera
    ))
    scene.render()
    with open(file_name, "w") as f:
        json.dump(json_dict, f, separators=(",", ":"))
