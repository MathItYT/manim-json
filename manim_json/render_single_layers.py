from manim_json.json_scene import JSONScene
from manim.scene.scene_file_writer import SceneFileWriter
from pathlib import Path
from manim import config


def render_single_layers(
    json_scene: JSONScene,
    prefix: str,
    directory: str = "videos",
    gray_scale: bool = False
):
    if Path(directory).exists() is False:
        Path(directory).mkdir()
    json_scene.renderer.file_writer.output_directory = Path(directory)
    json_scene.render()
    json_data = json_scene.data

    for i, layer in enumerate(json_scene.mobjects_from_data.keys(), start=1):
        new_json_data = {k: {} for k in json_data.keys()}
        for frame in list(json_data.keys()):
            for id_ in list(json_data[frame].keys()):
                if id_ == layer:
                    new_json_data[frame][id_] = json_data[frame][id_]

        new_json_scene = JSONScene()
        file_writer: SceneFileWriter = new_json_scene.renderer.file_writer
        out_format = "mov" if config.transparent else "mp4"
        if len(new_json_data) == 1:
            file_writer.image_file_path = Path(
                f"{directory}/{prefix}_{layer}.png"
            )
        elif len(new_json_data) > 1:
            file_writer.movie_file_path = Path(
                f"{directory}/{prefix}_{i}.{out_format}"
            )
        else:
            raise ValueError("No frames to render")
        new_json_scene.json_data = new_json_data
        new_json_scene.render()
