import init, { Scene, WasmColor, WasmGradientImageOrColor, WasmGradientStop, WasmLinearGradient, WasmVectorObject } from 'mathlikeanim-rs/browser';

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const playButton = document.getElementById('play');

const manimToCanvasCoords = (x, y) => {
  return [1080 / 8 * (x + 16 / 9 * 4), 1080 / 8 * (4 - y)];
};

const parseColor = (color, x1, y1, x2, y2) => {
  if (color.length == 1) {
    return WasmGradientImageOrColor.fromColor(rgbaToColor(color[0]));
  }
  return WasmGradientImageOrColor.fromLinearGradient(
    new WasmLinearGradient(
      x1,
      y1,
      x2,
      y2,
      color.map((rgba, i) => new WasmGradientStop(i / (color.length - 1), rgbaToColor(rgba))),
      1
    )
  );
};

const rgbaToColor = (rgba) => {
  const [r, g, b, a] = rgba;
  return new WasmColor(r, g, b, a);
};

const run = async () => {
  // Stream response
  const scene = new Scene(1920, 1080, 60);
  scene.setCanvasContext(ctx);
  const response = await fetch('/stream', { method: 'POST' });
  const reader = response.body.getReader();
  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    // Parse JSON
    const data = JSON.parse(new TextDecoder().decode(value));


    // Set background
    const { background, objects } = data;
    scene.clear();
    scene.setBackground(WasmGradientImageOrColor.fromColor(rgbaToColor(background)));
    for (let i = 0; i < objects.length; i++) {
      const obj = objects[i];
      const type = obj.type;
      if (type === 'VMobject') {
        let vecObj = new WasmVectorObject();
        let { points, fill, stroke, gradient_points, line_cap, line_join, stroke_width, background_stroke_width, background_stroke } = obj;
        const x1 = gradient_points[0][0];
        const y1 = gradient_points[0][1];
        const x2 = gradient_points[1][0];
        const y2 = gradient_points[1][1];
        if (background_stroke_width !== 0) {
          let backgroundObj = new WasmVectorObject();
          backgroundObj = backgroundObj.setPoints(points.map(([x, y]) => manimToCanvasCoords(x, y)));
          backgroundObj = backgroundObj.setStroke(parseColor(background_stroke, x1, y1, x2, y2), true);
          backgroundObj = backgroundObj.setStrokeWidth(background_stroke_width / 100 * canvas.height / 8, true);
          scene.add(backgroundObj.setIndex(2 * i));
        }
        vecObj = vecObj.setPoints(points.map(([x, y]) => manimToCanvasCoords(x, y)));
        vecObj = vecObj.setFill(parseColor(fill, x1, y1, x2, y2), true);
        vecObj = vecObj.setStroke(parseColor(stroke, x1, y1, x2, y2), true);
        vecObj = vecObj.setStrokeWidth(stroke_width / 100 * canvas.height / 8, true);
        vecObj = vecObj.setLineCap(line_cap, true);
        vecObj = vecObj.setLineJoin(line_join, true);
        scene.add(vecObj.setIndex(2 * i + 1));
      }
    }
    scene.renderFrame();
  }
};

playButton.onclick = () => init().then(run);
