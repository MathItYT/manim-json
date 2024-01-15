from manim_json import JSONScene, render_single_layers
from manim import config


config.disable_caching = True


class HelloWorld(JSONScene):
    json_data = "hello_world.json"


if __name__ == "__main__":
    render_single_layers(HelloWorld(), "hello_world")
