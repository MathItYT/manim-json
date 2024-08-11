import json
import time
import threading

from flask import Flask, Response, send_file

from manim.animation.creation import Create
from manim.mobject.geometry.arc import Circle

from manim_json.json_scene import JSONScene


app = Flask(__name__)


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
        circ = Circle()
        self.play(Create(circ))
        self.render_frame()
    
    def render_frame(self):
        self.wait(1 / self.camera.frame_rate)

    def tear_down(self):
        self.active = False
    
    def updater(self, dt):
        if self.stopped:
            raise StopIteration
    
    def stop(self):
        self.stopped = True
    
    def update_to_time(self, t: float):
        start_time = time.time()
        super().update_to_time(t)
        time.sleep(max(0, 1 / self.camera.frame_rate - time.time() + start_time))
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.active and not self.stopped:
            while self.frame_data is None and self.active and not self.stopped:
                time.sleep(0.0)
            if self.stopped or not self.active or self.frame_data is None:
                raise StopIteration  
            frame_data = self.frame_data
            self.frame_data = None
            return json.dumps(frame_data)
        raise StopIteration


scene: JSONScene | None = None


@app.route('/stream', methods=['POST'])
def stream():
    global scene
    if scene is not None:
        scene.stop()
    scene = ExampleScene()
    threading.Thread(target=scene.render).start()
    return Response(scene, mimetype='application/json')


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
    app.run()
