import json

from manim.scene.scene import Scene

from manim_json.json_camera import JSONCamera
from manim_json.json_renderer import JSONRenderer


class JSONScene(Scene):
    """A scene that outputs its data to a JSON file instead of rendering it.
    
    This is useful for web-based animations, where the data can be used to
    render the animation in a web browser.
    
    Parameters
    ----------
    json_file
        The file to save the JSON data to. If None, the data will not be saved.
    save_only_when_done
        If True, the data will only be saved when the scene is done.
    **kwargs
        Additional arguments to pass to the Scene constructor"""

    def __init__(
        self,
        json_file: str | None = None,
        save_only_when_done: bool = False,
        only_frame_data: bool = False,
        **kwargs
    ):
        self.json_file = json_file
        self.save_only_when_done = save_only_when_done
        self.only_frame_data = only_frame_data
        kwargs["renderer"] = JSONRenderer()
        kwargs["camera_class"] = JSONCamera
        super().__init__(**kwargs)
    
    def update_to_time(self, t: float):
        super().update_to_time(t)
        if self.json_file is not None and not self.save_only_when_done:
            with open(self.json_file, "w") as f:
                json.dump(self.renderer.data, f)
    
    def add_subcaption(self, content: str, duration: float = 1, offset: float = 0) -> None:
        pass

    def add_sound(self, sound_file: str, time_offset: float = 0, gain: float | None = None, **kwargs):
        pass
