from manim import *
from manim_json import render_json


config.disable_caching = True


class HelloWorld(Scene):
    def construct(self):
        circ = Circle()
        tex = Tex("Hello World!")
        self.play(Create(circ), Write(tex))
        self.wait()


if __name__ == "__main__":
    render_json(HelloWorld(), "hello_world.json")
