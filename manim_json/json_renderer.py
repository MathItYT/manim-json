from manim.animation.animation import Animation
from manim.mobject.mobject import Mobject
from manim.scene.scene import Scene

from manim_json.json_camera import JSONCamera


class JSONRenderer:
    """A renderer that outputs its data to a JSON file instead of rendering it.
    
    This is useful for web-based animations, where the data can be used to
    render the animation in a web browser.

    Attributes
    ----------
    data
        The data that will be saved to the JSON file.
    scene
        The scene being rendered.
    camera
        The camera used to capture the scene.
    frame_data
        The data for the current frame.
    time_in_frames
        The time in frames since the start of the animation.
    
    Methods
    -------
    deliver(data: dict) -> None
        Delivers the data for the current frame. Meant to be overridden.
    """

    def __init__(self):
        self.data = None
        self.camera = None
        self.time = 0.0
        self.num_plays = 0
        self.skip_animations = False
    
    def init_scene(self, scene: Scene):
        self.camera = JSONCamera()
        if not scene.only_frame_data:
            self.data = {
                "frames": [],
                "fps": self.camera.frame_rate,
                "frame_width": self.camera.frame_width,
                "frame_height": self.camera.frame_height,
                "pixel_width": self.camera.pixel_width,
                "pixel_height": self.camera.pixel_height
            }
        self.frame_data = {}
        self.time = 0.0
    
    def play(self, scene: Scene, *args: Animation, **kwargs):
        scene.compile_animation_data(*args, **kwargs)
        scene.begin_animations()
        scene.play_internal()

    def render(self, scene: Scene, t: float, moving_objects: list[Mobject]):
        self.frame_data["time"] = self.time
        background = self.camera.background.to_rgba_with_alpha(self.camera.background_opacity)
        self.frame_data["background"] = [background[0], background[1], background[2], background[3]]
        self.frame_data["objects"] = self.camera.get_objects_data(scene)
        if not scene.only_frame_data:
            self.data["frames"].append(self.frame_data)
        self.deliver(self.frame_data)
        self.frame_data = {}
        self.time += 1 / scene.camera.frame_rate
    
    def deliver(self, data: dict) -> None:
        """Delivers the data for the current frame. Meant to be overridden."""
        pass

    def scene_finished(self, scene: Scene) -> None:
        pass
