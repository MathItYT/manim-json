from manim_json import JSONScene, render_single_layers
from manim import config


config.transparent = True


class Graph(JSONScene):
    json_data = "graph_example.json"


if __name__ == "__main__":
    render_single_layers(Graph(), "graph")
