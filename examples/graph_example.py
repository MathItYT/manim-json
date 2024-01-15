from manim import *
from manim_json.render_json import render_json


config.disable_caching = True


class GraphExample(Scene):
    def construct(self):
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            x_length=6,
            y_length=6
        )
        self.add(axes)
        graph = axes.plot(lambda x: x**2/10)
        self.play(Create(graph))
        self.wait()


if __name__ == "__main__":
    render_json(GraphExample(), "graph_example.json")
