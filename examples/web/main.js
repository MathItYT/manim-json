import init, { Scene, WasmColor, WasmGradientImageOrColor, WasmGradientStop, WasmLinearGradient, WasmVectorObject } from 'mathlikeanim-rs/browser';

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const playButton = document.getElementById('play');
let scene;
let id;
let initialized = false;
let moving = false;
let busy = false;

const renderFrame = async (data) => {
  const { background, objects } = data;
  if (!id) {
    id = data.id;
  }
  scene.clear();

  // Set background color
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
};

const moveCircle = async (e) => {
  const boundingRect = e.target.getBoundingClientRect();
  const top = boundingRect.top;
  const left = boundingRect.left;
  const width = boundingRect.width;
  const height = boundingRect.height;
  const [x, y] = canvasToManimCoords(e.clientX * canvas.width / width - left, e.clientY * canvas.height / height - top);
  const json = await fetch('/move', { method: 'POST', body: JSON.stringify({ id, x, y }), headers: { 'Content-Type': 'application/json' } }).then(res => res.json());
  await renderFrame(json);
};

// When dragging the canvas, fire the event
canvas.onmousedown = async (e) => {
  moving = true;
  busy = true;
  await moveCircle(e);
  busy = false;
};

canvas.onmousemove = async (e) => {
  if (!moving || busy) {
    return;
  }
  busy = true;
  await moveCircle(e);
  busy = false;
};

canvas.onmouseup = () => {
  moving = false;
}

const manimToCanvasCoords = (x, y) => {
  return [1080 / 8 * (x + 16 / 9 * 4), 1080 / 8 * (4 - y)];
};

const canvasToManimCoords = (x, y) => {
  return [x / (1080 / 8) - 16 / 9 * 4, 4 - y / (1080 / 8)];
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
  if (!initialized) {
    await init();
    initialized = true;
  }
  if (id) {
    await fetch('/close', { method: 'POST', body: JSON.stringify({ id }), headers: { 'Content-Type': 'application/json' } });
    id = undefined;
  }
  // Stream response
  scene = new Scene(1920, 1080, 60);
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
    // Render frame
    await renderFrame(data);
  }
};

playButton.onclick = run;

window.onbeforeunload = async () => {
  await fetch('/close', { method: 'POST', body: JSON.stringify({ id }), headers: { 'Content-Type': 'application/json' } });
  id = undefined;
};
