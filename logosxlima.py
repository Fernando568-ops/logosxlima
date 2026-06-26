import streamlit as st
import streamlit.components.v1 as components
import anthropic
import json

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Design Studio",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Dark overall theme */
  .stApp { background: #0f1117; color: #e0e0e0; }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #30363d;
  }
  [data-testid="stSidebar"] * { color: #c9d1d9 !important; }

  /* Top bar */
  .top-bar {
    background: #161b22;
    border-bottom: 1px solid #30363d;
    padding: 10px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 0;
  }
  .top-bar h1 { font-size: 1.2rem; margin: 0; color: #58a6ff; font-family: monospace; }
  .top-bar span { font-size: 0.75rem; color: #8b949e; }

  /* Buttons */
  .stButton button {
    background: #21262d !important;
    color: #c9d1d9 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
    font-size: 0.82rem !important;
    padding: 4px 12px !important;
    transition: all 0.15s;
  }
  .stButton button:hover {
    background: #30363d !important;
    border-color: #58a6ff !important;
    color: #58a6ff !important;
  }

  /* Primary button */
  .stButton.primary button {
    background: #1f6feb !important;
    border-color: #1f6feb !important;
    color: #fff !important;
  }

  /* AI panel */
  .ai-panel {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px;
    height: 100%;
  }
  .ai-response {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 14px;
    font-size: 0.88rem;
    line-height: 1.65;
    color: #c9d1d9;
    max-height: 520px;
    overflow-y: auto;
    white-space: pre-wrap;
  }
  .section-label {
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #8b949e;
    margin-bottom: 6px;
    font-family: monospace;
  }
  div[data-testid="stTextInput"] input {
    background: #0d1117 !important;
    border: 1px solid #30363d !important;
    color: #c9d1d9 !important;
    border-radius: 6px !important;
    font-family: monospace;
    font-size: 0.82rem;
  }
  div[data-testid="stSelectbox"] select,
  div[data-testid="stSelectbox"] > div > div {
    background: #0d1117 !important;
    color: #c9d1d9 !important;
    border: 1px solid #30363d !important;
  }
  .stSlider > div > div > div { background: #1f6feb !important; }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] { background: #161b22; border-bottom: 1px solid #30363d; }
  .stTabs [data-baseweb="tab"] { color: #8b949e !important; }
  .stTabs [aria-selected="true"] { color: #58a6ff !important; border-bottom-color: #58a6ff !important; }

  /* Text area */
  textarea {
    background: #0d1117 !important;
    color: #c9d1d9 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
  }

  /* Hide default streamlit header */
  header[data-testid="stHeader"] { background: transparent; }
  #MainMenu, footer { visibility: hidden; }

  /* Badge */
  .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 600;
    background: #1f6feb22;
    color: #58a6ff;
    border: 1px solid #1f6feb44;
    margin-left: 8px;
  }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
if "scene_json" not in st.session_state:
    st.session_state.scene_json = json.dumps([])
if "ai_response" not in st.session_state:
    st.session_state.ai_response = ""
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ── THREE.JS 3D VIEWPORT ──────────────────────────────────────────────────────
THREE_CANVAS = """
<!DOCTYPE html>
<html>
<head>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#0d1117; overflow:hidden; font-family:monospace; }
canvas { display:block; }
#toolbar {
  position:absolute; top:12px; left:12px;
  display:flex; gap:6px; flex-wrap:wrap;
}
.btn {
  background:#21262d; color:#c9d1d9;
  border:1px solid #30363d; border-radius:5px;
  padding:5px 11px; font-size:11px; cursor:pointer;
  font-family:monospace; transition:all 0.15s;
}
.btn:hover, .btn.active { background:#1f6feb; border-color:#1f6feb; color:#fff; }
#status {
  position:absolute; bottom:10px; left:12px;
  font-size:10px; color:#8b949e; pointer-events:none;
  background:#0d111799; padding:4px 8px; border-radius:4px;
}
#info {
  position:absolute; top:12px; right:12px;
  font-size:10px; color:#8b949e;
  background:#0d111799; padding:6px 10px; border-radius:4px;
  text-align:right; line-height:1.7;
}
#scene-data { display:none; }
</style>
</head>
<body>
<div id="toolbar">
  <button class="btn active" id="btn-cube" onclick="addShape('cube')">⬜ Cube</button>
  <button class="btn" id="btn-sphere" onclick="addShape('sphere')">⚫ Sphere</button>
  <button class="btn" id="btn-cylinder" onclick="addShape('cylinder')">⬤ Cylinder</button>
  <button class="btn" id="btn-cone" onclick="addShape('cone')">▲ Cone</button>
  <button class="btn" id="btn-torus" onclick="addShape('torus')">◯ Torus</button>
  <button class="btn" id="btn-plane" onclick="addShape('plane')">▭ Plane</button>
  <span style="width:1px;background:#30363d;margin:0 2px"></span>
  <button class="btn" id="btn-move" onclick="setMode('move')">✥ Move</button>
  <button class="btn" id="btn-rotate" onclick="setMode('rotate')">↻ Rotate</button>
  <button class="btn" id="btn-scale" onclick="setMode('scale')">⇲ Scale</button>
  <span style="width:1px;background:#30363d;margin:0 2px"></span>
  <button class="btn" onclick="deleteSelected()">🗑 Delete</button>
  <button class="btn" onclick="clearScene()">✕ Clear</button>
</div>
<div id="info">
  Left-drag: Rotate view<br>
  Right-drag: Pan<br>
  Scroll: Zoom<br>
  Click object: Select<br>
  Drag handle: Transform
</div>
<div id="status">Ready — add a shape to begin</div>
<div id="scene-data"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ── Scene setup ────────────────────────────────────────────────
const W = window.innerWidth, H = window.innerHeight;
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(W, H);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0d1117);
scene.fog = new THREE.Fog(0x0d1117, 40, 100);

const camera = new THREE.PerspectiveCamera(60, W / H, 0.1, 200);
camera.position.set(6, 5, 8);
camera.lookAt(0, 0, 0);

// Lighting
const ambient = new THREE.AmbientLight(0x404060, 0.6);
scene.add(ambient);
const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
dirLight.position.set(8, 12, 6);
dirLight.castShadow = true;
dirLight.shadow.mapSize.width = 2048;
dirLight.shadow.mapSize.height = 2048;
scene.add(dirLight);
const fillLight = new THREE.DirectionalLight(0x4488ff, 0.3);
fillLight.position.set(-6, 2, -4);
scene.add(fillLight);

// Grid
const gridHelper = new THREE.GridHelper(20, 20, 0x30363d, 0x21262d);
scene.add(gridHelper);

// Axes
const axesHelper = new THREE.AxesHelper(2);
scene.add(axesHelper);

// Ground plane (invisible, for raycasting)
const groundGeo = new THREE.PlaneGeometry(40, 40);
const groundMat = new THREE.MeshBasicMaterial({ visible: false, side: THREE.DoubleSide });
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.name = '_ground';
scene.add(ground);

// ── State ──────────────────────────────────────────────────────
let objects = [];
let selected = null;
let transformMode = 'move';
let shapeCount = { cube:0, sphere:0, cylinder:0, cone:0, torus:0, plane:0 };

// Orbit controls (manual implementation)
let isOrbiting = false, isPanning = false;
let lastMouse = { x:0, y:0 };
let spherical = { theta: 0.6, phi: 1.0, r: 12 };

// Transform drag state
let isDragging = false;
let dragAxis = null;
let dragStart = null;
let objStartPos = null;
let objStartRot = null;
let objStartScale = null;

// Transform gizmo arrows
let gizmo = null;
const gizmoAxes = [];

// ── Materials ──────────────────────────────────────────────────
const COLORS = [0x4a9eff, 0xff6b6b, 0x6bff9e, 0xffd93d, 0xa78bfa, 0xfb923c, 0x34d399];
let colorIdx = 0;
function nextColor() { return COLORS[colorIdx++ % COLORS.length]; }

function makeGizmoArrow(color, direction, axis) {
  const group = new THREE.Group();
  group.userData.axis = axis;

  const lineGeo = new THREE.CylinderGeometry(0.04, 0.04, 1.4, 8);
  const lineMat = new THREE.MeshBasicMaterial({ color });
  const line = new THREE.Mesh(lineGeo, lineMat);

  const headGeo = new THREE.ConeGeometry(0.12, 0.35, 8);
  const headMat = new THREE.MeshBasicMaterial({ color });
  const head = new THREE.Mesh(headGeo, headMat);
  head.position.y = 0.88;

  group.add(line, head);

  if (axis === 'x') { group.rotation.z = -Math.PI/2; group.position.x = 0.9; }
  if (axis === 'y') { group.position.y = 0.9; }
  if (axis === 'z') { group.rotation.x = Math.PI/2; group.position.z = 0.9; }

  group.userData.color = color;
  group.userData.direction = direction;
  return group;
}

function createGizmo() {
  if (gizmo) scene.remove(gizmo);
  gizmo = new THREE.Group();
  gizmo.name = '_gizmo';

  gizmoAxes.length = 0;

  const ax = makeGizmoArrow(0xff4444, new THREE.Vector3(1,0,0), 'x');
  const ay = makeGizmoArrow(0x44ff44, new THREE.Vector3(0,1,0), 'y');
  const az = makeGizmoArrow(0x4488ff, new THREE.Vector3(0,0,1), 'z');

  gizmoAxes.push(ax, ay, az);
  gizmo.add(ax, ay, az);
  scene.add(gizmo);
}

function updateGizmo() {
  if (!selected || !gizmo) return;
  gizmo.position.copy(selected.position);
  const s = selected.scale.length() * 0.4 + 0.6;
  gizmo.scale.setScalar(s);
}

// ── Shape creation ─────────────────────────────────────────────
const SHAPES = {
  cube:     () => new THREE.BoxGeometry(1.2, 1.2, 1.2),
  sphere:   () => new THREE.SphereGeometry(0.7, 32, 32),
  cylinder: () => new THREE.CylinderGeometry(0.6, 0.6, 1.4, 32),
  cone:     () => new THREE.ConeGeometry(0.7, 1.4, 32),
  torus:    () => new THREE.TorusGeometry(0.6, 0.22, 16, 64),
  plane:    () => new THREE.PlaneGeometry(1.8, 1.8),
};

function addShape(type) {
  shapeCount[type] = (shapeCount[type] || 0) + 1;
  const geo = SHAPES[type]();
  const mat = new THREE.MeshStandardMaterial({
    color: nextColor(),
    roughness: 0.4,
    metalness: 0.15,
    transparent: false,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  mesh.position.set(
    (Math.random() - 0.5) * 4,
    0.7,
    (Math.random() - 0.5) * 4
  );
  mesh.userData = {
    type, id: Date.now(),
    name: type + '_' + shapeCount[type],
    color: '#' + mat.color.getHexString(),
  };
  scene.add(mesh);
  objects.push(mesh);
  selectObject(mesh);
  updateStatus('Added ' + mesh.userData.name);
  exportScene();
}

// ── Selection ──────────────────────────────────────────────────
function selectObject(obj) {
  if (selected && selected !== obj) {
    selected.material.emissive.setHex(0x000000);
  }
  selected = obj;
  if (selected) {
    selected.material.emissive.setHex(0x223355);
    createGizmo();
    updateGizmo();
    updateStatus('Selected: ' + selected.userData.name +
      ' | pos(' + selected.position.toArray().map(v=>v.toFixed(2)).join(', ') + ')');
  } else {
    if (gizmo) { scene.remove(gizmo); gizmo = null; }
  }
}

function deleteSelected() {
  if (!selected) return;
  scene.remove(selected);
  objects = objects.filter(o => o !== selected);
  if (gizmo) { scene.remove(gizmo); gizmo = null; }
  selected = null;
  updateStatus('Object deleted');
  exportScene();
}

function clearScene() {
  objects.forEach(o => scene.remove(o));
  objects = [];
  if (gizmo) { scene.remove(gizmo); gizmo = null; }
  selected = null;
  shapeCount = {};
  colorIdx = 0;
  updateStatus('Scene cleared');
  exportScene();
}

// ── Mode ───────────────────────────────────────────────────────
function setMode(m) {
  transformMode = m;
  ['move','rotate','scale'].forEach(mode => {
    document.getElementById('btn-' + mode).classList.toggle('active', mode === m);
  });
  updateStatus('Mode: ' + m);
}

// ── Raycasting ─────────────────────────────────────────────────
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function getIntersects(event, targets) {
  const rect = renderer.domElement.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  return raycaster.intersectObjects(targets, true);
}

// ── Export scene to host ───────────────────────────────────────
function exportScene() {
  const data = objects.map(o => ({
    name: o.userData.name,
    type: o.userData.type,
    position: o.position.toArray().map(v => +v.toFixed(3)),
    rotation: o.rotation.toArray().slice(0,3).map(v => +v.toFixed(3)),
    scale: o.scale.toArray().map(v => +v.toFixed(3)),
    color: '#' + o.material.color.getHexString(),
  }));
  document.getElementById('scene-data').innerText = JSON.stringify(data);
  // Post to Streamlit
  window.parent.postMessage({ type: 'scene_update', data: JSON.stringify(data) }, '*');
}

// ── Mouse events ───────────────────────────────────────────────
let mouseDownPos = { x:0, y:0 };

renderer.domElement.addEventListener('mousedown', e => {
  mouseDownPos = { x: e.clientX, y: e.clientY };

  // Check gizmo first
  if (selected && gizmo) {
    const hits = getIntersects(e, gizmoAxes);
    if (hits.length > 0) {
      isDragging = true;
      dragAxis = hits[0].object.parent.userData.axis;
      dragStart = { x: e.clientX, y: e.clientY };
      objStartPos = selected.position.clone();
      objStartRot = selected.rotation.clone();
      objStartScale = selected.scale.clone();
      return;
    }
  }

  if (e.button === 0) { isOrbiting = true; }
  if (e.button === 2) { isPanning = true; }
  lastMouse = { x: e.clientX, y: e.clientY };
});

renderer.domElement.addEventListener('mouseup', e => {
  if (isDragging) { isDragging = false; dragAxis = null; exportScene(); return; }
  isOrbiting = false; isPanning = false;

  const dx = Math.abs(e.clientX - mouseDownPos.x);
  const dy = Math.abs(e.clientY - mouseDownPos.y);
  if (dx < 4 && dy < 4) {
    const hits = getIntersects(e, objects);
    if (hits.length > 0) { selectObject(hits[0].object); }
    else if (e.button === 0) { selectObject(null); }
  }
});

renderer.domElement.addEventListener('mousemove', e => {
  if (isDragging && selected && dragAxis) {
    const dx = (e.clientX - dragStart.x) * 0.018;
    const dy = -(e.clientY - dragStart.y) * 0.018;
    const delta = Math.abs(dx) > Math.abs(dy) ? dx : dy;

    if (transformMode === 'move') {
      const pos = objStartPos.clone();
      if (dragAxis === 'x') pos.x += dx * 1.8;
      if (dragAxis === 'y') pos.y += dy * 1.8;
      if (dragAxis === 'z') pos.z += dx * 1.8;
      selected.position.copy(pos);
    } else if (transformMode === 'rotate') {
      const rot = objStartRot.clone();
      if (dragAxis === 'x') rot.x += delta * 2;
      if (dragAxis === 'y') rot.y += delta * 2;
      if (dragAxis === 'z') rot.z += delta * 2;
      selected.rotation.copy(rot);
    } else if (transformMode === 'scale') {
      const sc = objStartScale.clone();
      const factor = 1 + delta;
      if (dragAxis === 'x') sc.x = Math.max(0.1, objStartScale.x * factor);
      if (dragAxis === 'y') sc.y = Math.max(0.1, objStartScale.y * factor);
      if (dragAxis === 'z') sc.z = Math.max(0.1, objStartScale.z * factor);
      selected.scale.copy(sc);
    }
    updateGizmo();
    return;
  }

  if (isOrbiting) {
    spherical.theta -= (e.clientX - lastMouse.x) * 0.008;
    spherical.phi -= (e.clientY - lastMouse.y) * 0.008;
    spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));
  }
  if (isPanning) {
    const panSpeed = 0.015 * spherical.r / 8;
    const right = new THREE.Vector3().crossVectors(
      new THREE.Vector3(
        Math.sin(spherical.phi)*Math.sin(spherical.theta),
        Math.cos(spherical.phi),
        Math.sin(spherical.phi)*Math.cos(spherical.theta)
      ),
      new THREE.Vector3(0,1,0)
    ).normalize();
    camera.position.addScaledVector(right, -(e.clientX - lastMouse.x) * panSpeed);
    camera.position.y += (e.clientY - lastMouse.y) * panSpeed;
  }
  lastMouse = { x: e.clientX, y: e.clientY };
});

renderer.domElement.addEventListener('wheel', e => {
  spherical.r *= 1 + e.deltaY * 0.001;
  spherical.r = Math.max(2, Math.min(60, spherical.r));
});
renderer.domElement.addEventListener('contextmenu', e => e.preventDefault());

// ── Camera orbit update ────────────────────────────────────────
const target = new THREE.Vector3(0, 0, 0);
function updateCamera() {
  camera.position.x = target.x + spherical.r * Math.sin(spherical.phi) * Math.sin(spherical.theta);
  camera.position.y = target.y + spherical.r * Math.cos(spherical.phi);
  camera.position.z = target.z + spherical.r * Math.sin(spherical.phi) * Math.cos(spherical.theta);
  camera.lookAt(target);
}

// ── Status ─────────────────────────────────────────────────────
function updateStatus(msg) {
  document.getElementById('status').innerText = msg;
}

// ── Resize ─────────────────────────────────────────────────────
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ── Render loop ────────────────────────────────────────────────
function animate() {
  requestAnimationFrame(animate);
  updateCamera();
  if (selected && gizmo) updateGizmo();
  renderer.render(scene, camera);
}
animate();

// ── Listen for scene request from parent ──────────────────────
window.addEventListener('message', e => {
  if (e.data && e.data.type === 'get_scene') { exportScene(); }
  if (e.data && e.data.type === 'set_color' && selected) {
    selected.material.color.set(e.data.color);
    selected.userData.color = e.data.color;
    exportScene();
  }
});
</script>
</body>
</html>
"""

# ── Layout ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
  <h1>🧊 AI Design Studio</h1>
  <span>SketchUp-style 3D modeler with AI design analysis</span>
  <span class="badge">powered by Claude</span>
</div>
""", unsafe_allow_html=True)

# Two-column layout: viewport | AI panel
col_viewport, col_ai = st.columns([3, 1.1])

with col_viewport:
    components.html(THREE_CANVAS, height=620, scrolling=False)

with col_ai:
    st.markdown('<div class="ai-panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">⚙ API Configuration</div>', unsafe_allow_html=True)

    api_key = st.text_input(
        "Anthropic API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-ant-...",
        label_visibility="collapsed",
    )
    if api_key:
        st.session_state.api_key = api_key

    st.markdown("---")
    st.markdown('<div class="section-label">📋 Scene Description</div>', unsafe_allow_html=True)

    scene_input = st.text_area(
        "Scene JSON (paste from viewport or type manually)",
        value=st.session_state.scene_json,
        height=130,
        help="This is auto-populated when you interact with the canvas above. You can also paste a JSON scene description.",
        label_visibility="collapsed",
        placeholder='[{"name":"cube_1","type":"cube","position":[0,0.7,0],...}]',
    )
    if scene_input:
        st.session_state.scene_json = scene_input

    st.markdown('<div class="section-label">🎯 Analysis Mode</div>', unsafe_allow_html=True)
    analysis_mode = st.selectbox(
        "Analysis mode",
        [
            "General Design Review",
            "Structural Analysis",
            "Aesthetic & Composition",
            "Optimization Suggestions",
            "Architecture Critique",
            "Interior Design Feedback",
        ],
        label_visibility="collapsed",
    )

    custom_prompt = st.text_area(
        "Custom question (optional)",
        placeholder="e.g. Does this look like a good office layout?",
        height=70,
        label_visibility="collapsed",
    )

    analyze_btn = st.button("🔍 Analyze Design", use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-label">🤖 AI Feedback</div>', unsafe_allow_html=True)

    if analyze_btn:
        if not st.session_state.api_key:
            st.error("Please enter your Anthropic API key above.")
        elif not st.session_state.scene_json or st.session_state.scene_json == "[]":
            st.warning("No scene data found. Add shapes in the canvas, then paste the scene JSON here.")
        else:
            with st.spinner("Analyzing your design..."):
                try:
                    scene_data = json.loads(st.session_state.scene_json)

                    # Build a human-readable scene description
                    scene_text = f"3D Scene with {len(scene_data)} object(s):\n"
                    for obj in scene_data:
                        scene_text += (
                            f"\n• {obj.get('name','object')} ({obj.get('type','unknown')})\n"
                            f"  Position: x={obj.get('position',[0,0,0])[0]}, "
                            f"y={obj.get('position',[0,0,0])[1]}, "
                            f"z={obj.get('position',[0,0,0])[2]}\n"
                            f"  Scale: {obj.get('scale',[1,1,1])}\n"
                            f"  Color: {obj.get('color','unknown')}\n"
                        )

                    mode_prompts = {
                        "General Design Review": "Give a holistic review of this 3D scene. Comment on composition, balance, use of space, and overall design quality.",
                        "Structural Analysis": "Analyze the structural integrity and spatial logic of this arrangement. Are the objects placed in physically sensible positions?",
                        "Aesthetic & Composition": "Evaluate the aesthetic quality and composition. Comment on color harmony, visual balance, and whether the arrangement is visually pleasing.",
                        "Optimization Suggestions": "Suggest specific improvements to this design. How could the objects be repositioned, scaled, or replaced to improve the design?",
                        "Architecture Critique": "Critique this design as an architect would. Consider proportions, spatial flow, and how the forms relate to each other.",
                        "Interior Design Feedback": "Analyze this as an interior designer. Comment on furniture arrangement logic, space utilization, and room feel.",
                    }

                    base_prompt = mode_prompts[analysis_mode]
                    full_prompt = (
                        f"You are an expert 3D designer and design critic.\n\n"
                        f"Analyze the following 3D scene described in JSON:\n\n"
                        f"{scene_text}\n\n"
                        f"Raw JSON: {st.session_state.scene_json}\n\n"
                        f"Task: {base_prompt}\n"
                    )
                    if custom_prompt.strip():
                        full_prompt += f"\nAdditionally, the user asks: {custom_prompt.strip()}"

                    full_prompt += (
                        "\n\nBe specific and constructive. Use short paragraphs. "
                        "Reference actual object names and positions from the scene data. "
                        "Keep the response under 400 words."
                    )

                    client = anthropic.Anthropic(api_key=st.session_state.api_key)
                    message = client.messages.create(
                        model="claude-opus-4-6",
                        max_tokens=600,
                        messages=[{"role": "user", "content": full_prompt}],
                    )
                    st.session_state.ai_response = message.content[0].text

                except json.JSONDecodeError:
                    st.session_state.ai_response = "⚠ Invalid JSON in scene data. Make sure to paste valid scene JSON."
                except anthropic.AuthenticationError:
                    st.session_state.ai_response = "⚠ Invalid API key. Please check your Anthropic API key."
                except Exception as ex:
                    st.session_state.ai_response = f"⚠ Error: {str(ex)}"

    if st.session_state.ai_response:
        st.markdown(
            f'<div class="ai-response">{st.session_state.ai_response}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="ai-response" style="color:#444;font-style:italic;">'
            'AI feedback will appear here after you analyze a scene.'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ── How to use instructions ────────────────────────────────────────────────────
with st.expander("📖 How to use"):
    st.markdown("""
**1. Build your scene**
- Use the toolbar buttons in the 3D viewport to add shapes (Cube, Sphere, Cylinder, Cone, Torus, Plane)
- Click an object to select it (it highlights blue)
- Use **Move / Rotate / Scale** mode + drag the colored arrows to transform objects

**2. Export the scene**
- After building, open your browser's developer console (F12) and run:
  ```javascript
  document.getElementById('scene-data').innerText
  ```
- Copy the JSON output and paste it into the **Scene Description** text area on the right sidebar

**3. Get AI analysis**
- Enter your Anthropic API key
- Choose an analysis mode
- Optionally add a custom question
- Click **Analyze Design**

**Controls:**
| Action | Control |
|---|---|
| Rotate view | Left-click drag |
| Pan view | Right-click drag |
| Zoom | Scroll wheel |
| Select object | Left-click on object |
| Transform | Drag colored axis arrows |
""")
