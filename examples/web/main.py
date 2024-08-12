from __future__ import annotations

import json
import time
import threading

from flask import Flask, Response, send_file, request, jsonify

from manim.animation.creation import Create
from manim.mobject.geometry.arc import Circle
from manim.constants import UP, RIGHT

from manim_json.json_scene import JSONScene


app = Flask(__name__)
scenes: dict[int, ExampleScene] = {}
threads: dict[int, threading.Thread] = {}


class ExampleScene(JSONScene):
    def __init__(
        self,
        json_file: str | None = None,
        save_only_when_done: bool = False,
        only_frame_data: bool = False,
        **kwargs
    ):
        super().__init__(json_file, save_only_when_done, only_frame_data, **kwargs)
        self.stopped = False
        self.active = True
        self.frame_data = {
            "time": 0.0,
            "objects": [],
            "background": [0.0, 0.0, 0.0, 1.0]
        }
        self.renderer.deliver = lambda data: self.deliver(data)

    def deliver(self, data: dict):
        self.frame_data = data

    def construct(self):
        self.circ = Circle()
        self.play(Create(self.circ))
        self.render_frame()
        self.stop()
    
    def render_frame(self):
        self.wait(1 / self.camera.frame_rate)
    
    def stop(self):
        self.stopped = True
    
    def update_to_time(self, t: float):
        start_time = time.time()
        super().update_to_time(t)
        time.sleep(max(0, 1 / self.camera.frame_rate - time.time() + start_time))
    
    def move_circle(self, x: float, y: float):
        self.circ.move_to(x * RIGHT + y * UP)
        self.render_frame()
    
    def __iter__(self):
        return self
    
    def __next__(self):
        global scenes
        if self.active and not self.stopped:
            while self.frame_data is None and self.active and not self.stopped:
                time.sleep(0.0)
            if self.stopped or not self.active or self.frame_data is None:
                raise StopIteration  
            frame_data = self.frame_data
            frame_data["id"] = id(self)
            self.frame_data = None
            return json.dumps(frame_data)
        raise StopIteration


@app.route('/stream', methods=['POST'])
def stream():
    global scenes
    scene = ExampleScene()
    threads[id(scene)] = threading.Thread(target=scene.render)
    threads[id(scene)].start()
    scenes[id(scene)] = scene
    return Response(scene, mimetype='application/json')


@app.route('/close', methods=['POST'])
def close():
    global scenes, threads
    id_ = int(request.json['id'])
    threads[id_].join()
    del threads[id_]
    del scenes[id_]
    return 'OK'


@app.route('/move', methods=['POST'])
def move():
    global scenes
    id_ = int(request.json['id'])
    x = float(request.json['x'])
    y = float(request.json['y'])
    scenes[id_].move_circle(x, y)
    frame_data = scenes[id_].frame_data
    scenes[id_].frame_data = None
    return jsonify(frame_data)


@app.route('/', methods=['GET'])
def index():
    return send_file('index.html')


@app.route('/style.css', methods=['GET'])
def style():
    return send_file('style.css')


@app.route('/main.js', methods=['GET'])
def main_js():
    return send_file('main.js')


@app.route('/mathlikeanim-rs/browser/mathlikeanim_rs.js', methods=['GET'])
def mathlikeanim_rs():
    return send_file('node_modules/mathlikeanim-rs/browser/mathlikeanim_rs.js')


@app.route('/mathlikeanim-rs/browser/mathlikeanim_rs_bg.wasm', methods=['GET'])
def mathlikeanim_rs_bg():
    return send_file('node_modules/mathlikeanim-rs/browser/mathlikeanim_rs_bg.wasm')


if __name__ == '__main__':
    app.run(port=3000)
