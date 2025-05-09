// 使用全局 PIXI.live2d 提供的 Live2DModel
// 使用全局 PIXI.live2d 提供的 Live2DModel
// 使用全局 PIXI.live2d 提供的 Live2DModel
const { Live2DModel } = PIXI.live2d;

const canvas = document.getElementById('canvas');
const app = new PIXI.Application({
  view: canvas,
  width: window.innerWidth,
  height: window.innerHeight,
  transparent: true,
  autoStart: true
});

window.addEventListener('resize', () => {
  app.renderer.resize(window.innerWidth, window.innerHeight);
});

let model, isDragging = false;
let dragOffset = { x: 0, y: 0 };

// Helpers
function getModelBounds() {
  const w = model.width * model.scale.x;
  const h = model.height * model.scale.y;
  const left = model.x - w * model.anchor.x;
  const right = left + w;
  const top = model.y - h * model.anchor.y;
  const bottom = top + h;
  return { left, right, top, bottom };
}

function isPointInModel(x, y) {
  if (!model) return false;
  const b = getModelBounds();
  return x >= b.left && x <= b.right && y >= b.top && y <= b.bottom;
}

// Load model
// 注意：确保模型文件名及路径与 project 目录一致，避免空格
const modelUrl = 'model/whitecatfree_vts/sdwhite cat free.model3.json';
Live2DModel.from(encodeURI(modelUrl))
  .then(m => {
    model = m;
    model.anchor.set(0.5, 0.5);
    model.scale.set(0.25);
    model.x = window.innerWidth / 2;
    model.y = window.innerHeight / 2;
    model.interactive = true;
    model.buttonMode = true;

    app.stage.addChild(model);
    model.on('pointerdown', onDragStart);
  })
  .catch(err => console.error('Model load error:', err));

// Drag handlers
function onDragStart(e) {
  isDragging = true;
  const pos = e.data.global;
  dragOffset.x = pos.x - model.x;
  dragOffset.y = pos.y - model.y;
  window.addEventListener('pointermove', onDragMove, { passive: true });
  window.addEventListener('pointerup', onDragEnd, { passive: true });
}

function onDragMove(e) {
  if (!isDragging) return;
  model.x = e.clientX - dragOffset.x;
  model.y = e.clientY - dragOffset.y;
}

function onDragEnd() {
  isDragging = false;
  window.removeEventListener('pointermove', onDragMove);
  window.removeEventListener('pointerup', onDragEnd);
}

// Zoom with wheel (passive: false to allow preventDefault)
window.addEventListener('wheel', e => {
  if (!model || !isPointInModel(e.clientX, e.clientY)) return;
  e.preventDefault();
  const scaleFactor = e.deltaY < 0 ? 1.05 : 0.95;
  const newScale = Math.min(Math.max(model.scale.x * scaleFactor, 0.1), 2);
  model.scale.set(newScale);
}, { passive: false });

