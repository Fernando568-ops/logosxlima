import streamlit as st
import streamlit.components.v1 as components

# ============================================================
#  API CONFIGURATION — reads from st.secrets (OpenRouter)
#  Set in .streamlit/secrets.toml:
#    OPENROUTER_API_KEY = "sk-or-..."
#    OPENROUTER_MODEL   = "anthropic/claude-3.5-sonnet"  # optional
# ============================================================
try:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
except (KeyError, FileNotFoundError):
    OPENROUTER_API_KEY = ""

try:
    OPENROUTER_MODEL = st.secrets["OPENROUTER_MODEL"]
except (KeyError, FileNotFoundError):
    OPENROUTER_MODEL = "anthropic/claude-sonnet-4-6"

# ============================================================

st.set_page_config(page_title="AI CAD Studio", layout="wide", page_icon="📐")

st.markdown("""
<style>
body, .stApp { background:#0a0e14 !important; color:#e6edf3; }
[data-testid="stSidebar"] { background:#0f1318 !important; border-right:1px solid #1e2530; }
[data-testid="stSidebar"] label,[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,[data-testid="stSidebar"] div { color:#c9d1d9 !important; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color:#8fa3c0 !important; font-size:11px !important; text-transform:uppercase; letter-spacing:0.1em; }
.stButton > button {
  background:#131920; color:#9aabbc; border:1px solid #1e2d3d;
  border-radius:4px; font-size:11px; width:100%; margin:1px 0;
  padding:5px 8px; font-family:monospace; transition:all 0.12s;
}
.stButton > button:hover { background:#1a2840; border-color:#3a6ea8; color:#c8d8e8; }
.stSelectbox > div > div { background:#0f1318 !important; border-color:#1e2530 !important; font-size:12px; }
.stRadio > div { flex-direction:row !important; }
.stRadio label { font-size:11px !important; }
footer, header, #MainMenu { visibility:hidden; }
.block-container { padding-top:0.4rem; }
div[data-testid="stNumberInput"] input { background:#0f1318 !important; color:#c9d1d9 !important; border-color:#1e2530 !important; font-family:monospace; font-size:12px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📐 AI CAD Studio")
    st.markdown("---")

    # API Status
    if OPENROUTER_API_KEY:
        st.markdown(f"""
        <div style='background:#0d2a1a;border:1px solid #1a5c35;border-radius:4px;
        padding:6px 10px;font-size:11px;color:#3fb97a;font-family:monospace;margin-bottom:8px;'>
        ✓ OpenRouter connected<br>
        <span style='color:#4a7a5a;font-size:10px;'>{OPENROUTER_MODEL}</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#2a0d0d;border:1px solid #5c1a1a;border-radius:4px;
        padding:6px 10px;font-size:11px;color:#e05555;font-family:monospace;margin-bottom:8px;'>
        ✗ No API key found<br>
        <span style='color:#7a4a4a;font-size:10px;'>Add OPENROUTER_API_KEY to secrets.toml</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("### ➕ Primitives")
    c1, c2 = st.columns(2)
    with c1:
        add_cube      = st.button("⬛ Box")
        add_cylinder  = st.button("⬤ Cylinder")
        add_cone      = st.button("▲ Cone")
        add_wedge     = st.button("◤ Wedge")
    with c2:
        add_sphere    = st.button("● Sphere")
        add_torus     = st.button("⭕ Torus")
        add_plane     = st.button("▭ Plane")
        add_pipe      = st.button("| Pipe")

    st.markdown("---")
    st.markdown("### 🎮 Transform")
    mode = st.radio("", ["Move","Rotate","Scale"], horizontal=True, label_visibility="collapsed")
    world_local = st.radio("Space", ["World","Local"], horizontal=True)

    st.markdown("---")
    st.markdown("### 📏 CAD Tools")
    c3, c4 = st.columns(2)
    with c3:
        toggle_grid   = st.button("# Snap Grid")
        toggle_wire   = st.button("⬡ Wireframe")
        toggle_bbox   = st.button("⬜ Bbox")
        toggle_dims   = st.button("↔ Dimensions")
    with c4:
        toggle_normals = st.button("↑ Normals")
        toggle_axes    = st.button("+ Origin")
        toggle_measure = st.button("📐 Measure")
        toggle_section = st.button("✂ Section")

    st.markdown("---")
    st.markdown("### 📊 Transform Values")
    st.markdown("<div style='font-size:10px;color:#4a6080;margin-bottom:4px;font-family:monospace;'>Position (X / Y / Z)</div>", unsafe_allow_html=True)
    tp1, tp2, tp3 = st.columns(3)
    with tp1: pos_x = st.number_input("X", value=0.0, step=0.1, format="%.2f", label_visibility="collapsed", key="px")
    with tp2: pos_y = st.number_input("Y", value=0.0, step=0.1, format="%.2f", label_visibility="collapsed", key="py")
    with tp3: pos_z = st.number_input("Z", value=0.0, step=0.1, format="%.2f", label_visibility="collapsed", key="pz")
    apply_transform = st.button("↳ Apply Position")

    st.markdown("---")
    st.markdown("### 🗂️ Layers")
    layer_name = st.selectbox("Active Layer", ["Layer 0", "Construction", "Hidden", "Dimensions", "Section"], label_visibility="collapsed")
    c5, c6 = st.columns(2)
    with c5: toggle_layer_vis = st.button("👁 Toggle")
    with c6: toggle_layer_lock = st.button("🔒 Lock")

    st.markdown("---")
    st.markdown("### 🎨 Material")
    col_mat, col_rough = st.columns(2)
    with col_mat: color_pick = st.color_picker("Color", "#4a9eff", label_visibility="collapsed")
    with col_rough: roughness = st.slider("Rough", 0.0, 1.0, 0.38, label_visibility="collapsed")
    c7, c8 = st.columns(2)
    with c7: metalness = st.slider("Metal", 0.0, 1.0, 0.18, label_visibility="collapsed")
    with c8: apply_mat = st.button("Apply Mat.")

    st.markdown("---")
    st.markdown("### 🗑️ Scene")
    cd1, cd2, cd3 = st.columns(3)
    with cd1: delete_sel = st.button("🗑 Del")
    with cd2: duplicate_sel = st.button("⧉ Dup")
    with cd3: clear_all = st.button("✕ Clear")

    st.markdown("---")
    st.markdown("### 🤖 AI Analysis")
    analysis_mode = st.selectbox("Mode", [
        "General Design Review",
        "Structural Analysis",
        "Dimensional Check",
        "GD&T Suggestions",
        "Aesthetic & Composition",
        "Manufacturing Feasibility",
        "FEA Pre-check",
        "Assembly Notes",
    ], label_visibility="collapsed")
    ai_detail = st.radio("Detail", ["Brief","Detailed"], horizontal=True)
    st.markdown("""
    <div style='background:#0d1e30;border:1px solid #1a3d5c;border-radius:4px;
    padding:8px 10px;font-size:11px;color:#4a8ab8;margin-top:6px;font-family:monospace;'>
    [X] Analyze selected object<br>
    [M] Measure mode toggle<br>
    [G] Toggle snap grid<br>
    [W] Wireframe toggle<br>
    [Del] Delete selected<br>
    [D] Duplicate selected<br>
    [F] Frame selected<br>
    [Esc] Deselect / close
    </div>
    """, unsafe_allow_html=True)

# ── JS command router ─────────────────────────────────────────
js_cmd = "null"
if add_cube:           js_cmd = "'addShape:box'"
elif add_sphere:       js_cmd = "'addShape:sphere'"
elif add_cylinder:     js_cmd = "'addShape:cylinder'"
elif add_cone:         js_cmd = "'addShape:cone'"
elif add_torus:        js_cmd = "'addShape:torus'"
elif add_plane:        js_cmd = "'addShape:plane'"
elif add_wedge:        js_cmd = "'addShape:wedge'"
elif add_pipe:         js_cmd = "'addShape:pipe'"
elif delete_sel:       js_cmd = "'deleteSelected'"
elif duplicate_sel:    js_cmd = "'duplicateSelected'"
elif clear_all:        js_cmd = "'clearScene'"
elif apply_mat:        js_cmd = f"'setMaterial:{color_pick}:{roughness:.2f}:{metalness:.2f}'"
elif toggle_grid:      js_cmd = "'toggleSnapGrid'"
elif toggle_wire:      js_cmd = "'toggleWireframe'"
elif toggle_bbox:      js_cmd = "'toggleBbox'"
elif toggle_dims:      js_cmd = "'toggleDimensions'"
elif toggle_normals:   js_cmd = "'toggleNormals'"
elif toggle_axes:      js_cmd = "'toggleOriginAxes'"
elif toggle_measure:   js_cmd = "'toggleMeasureMode'"
elif toggle_section:   js_cmd = "'toggleSection'"
elif toggle_layer_vis: js_cmd = f"'layerVis:{layer_name}'"
elif toggle_layer_lock:js_cmd = f"'layerLock:{layer_name}'"
elif apply_transform:  js_cmd = f"'applyPosition:{pos_x:.3f}:{pos_y:.3f}:{pos_z:.3f}'"

mode_js    = {"Move":"move","Rotate":"rotate","Scale":"scale"}[mode]
space_js   = "world" if world_local == "World" else "local"
detail_js  = "detailed" if ai_detail == "Detailed" else "brief"

# ── Full self-contained CAD HTML application ──────────────────
HTML = f"""<!DOCTYPE html>
<html>
<head>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0a0e14; overflow:hidden; font-family:'Courier New',monospace; user-select:none; }}
canvas {{ display:block; }}

/* ── HUD / Overlays ── */
#coord-display {{
  position:absolute; top:10px; left:10px;
  background:#0a0e14cc; border:1px solid #1e2530; border-radius:3px;
  padding:6px 12px; font-size:10px; color:#4a7a9a; line-height:1.9;
  pointer-events:none; min-width:220px;
}}
#coord-display .label {{ color:#1e4060; }}
#coord-display .value {{ color:#5a9ac0; }}
#coord-display .selected-name {{ color:#3a7ab8; font-size:11px; font-weight:bold; }}

#status-bar {{
  position:absolute; bottom:0; left:0; right:0;
  background:#0a0e14ee; border-top:1px solid #1e2530;
  display:flex; align-items:center; gap:0;
  font-size:10px; color:#3a5a78; height:26px;
}}
.status-cell {{
  padding:0 12px; height:100%; display:flex; align-items:center;
  border-right:1px solid #1a2030;
}}
.status-cell.active {{ color:#5a9ac0; }}
.status-cell.warn {{ color:#c09030; }}

/* ── Properties Panel ── */
#props-panel {{
  position:absolute; top:10px; right:10px; width:220px;
  background:#0a0e14ee; border:1px solid #1e2530; border-radius:3px;
  font-size:10px; display:none;
}}
#props-header {{
  padding:6px 10px; border-bottom:1px solid #1a2030;
  color:#4a7a9a; font-size:10px; text-transform:uppercase; letter-spacing:0.08em;
  display:flex; justify-content:space-between; align-items:center;
}}
#props-body {{ padding:8px 10px; }}
.prop-row {{ display:flex; justify-content:space-between; margin:3px 0; }}
.prop-label {{ color:#2a4a62; }}
.prop-val {{ color:#5a9ac0; font-family:monospace; }}
.prop-section {{ color:#1e3a52; text-transform:uppercase; letter-spacing:0.06em;
  font-size:9px; margin:6px 0 2px; border-bottom:1px solid #1a2030; padding-bottom:2px; }}

/* ── Measurement Display ── */
#measure-panel {{
  position:absolute; top:10px; left:50%; transform:translateX(-50%);
  background:#0a1820ee; border:1px solid #1a4060; border-radius:3px;
  padding:6px 16px; font-size:11px; color:#40a0d0; display:none;
  pointer-events:none; text-align:center;
}}

/* ── AI Panel ── */
#ai-panel {{
  position:absolute; bottom:36px; right:10px; width:360px;
  background:#0a0e14f0; border:1px solid #1e2530; border-radius:3px;
  display:none; flex-direction:column; max-height:50vh;
  box-shadow:0 4px 24px #000000aa;
}}
#ai-header {{
  display:flex; align-items:center; justify-content:space-between;
  padding:7px 12px; border-bottom:1px solid #1a2030;
}}
#ai-header span {{ color:#3a7ab8; font-size:10px; letter-spacing:0.1em; text-transform:uppercase; }}
#ai-close {{
  background:none; border:none; color:#2a4a62; cursor:pointer;
  font-size:14px; padding:0 4px; line-height:1;
}}
#ai-close:hover {{ color:#e6edf3; }}
#ai-body {{
  padding:12px; overflow-y:auto; flex:1;
  font-size:11px; color:#8a9ab0; line-height:1.8;
}}
#ai-body .obj-tag {{
  background:#0d1e30; border:1px solid #1a3d5c;
  border-radius:2px; padding:3px 8px; font-size:9px;
  color:#3a7ab8; margin-bottom:8px; display:inline-block;
  text-transform:uppercase; letter-spacing:0.06em;
}}
.ai-section-head {{
  color:#2a6a9a; font-size:9px; text-transform:uppercase;
  letter-spacing:0.08em; margin:8px 0 2px;
  border-bottom:1px solid #1a2030; padding-bottom:2px;
}}
.loading-row {{ display:flex; align-items:center; gap:8px; color:#2a4a62; }}
.dot {{ animation:blink 1.4s infinite; }}
.dot:nth-child(2){{ animation-delay:0.2s; }}
.dot:nth-child(3){{ animation-delay:0.4s; }}
@keyframes blink{{ 0%,80%,100%{{opacity:0;}} 40%{{opacity:1;}} }}

/* ── Section plane indicator ── */
#section-indicator {{
  position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
  pointer-events:none; display:none;
  border:1px dashed #3a6aa0; width:300px; height:300px; opacity:0.3;
}}

/* ── Snap indicator ── */
#snap-dot {{
  position:absolute; width:8px; height:8px;
  background:#40c040; border-radius:50%; pointer-events:none;
  display:none; transform:translate(-4px,-4px);
}}
</style>
</head>
<body>

<!-- HUD: coordinate + object info -->
<div id="coord-display">
  <div><span class="label">CURSOR  </span><span class="value" id="cursor-pos">--</span></div>
  <div><span class="label">CAMERA  </span><span class="value" id="cam-pos">--</span></div>
  <div><span class="label">OBJECTS </span><span class="value" id="obj-count">0</span></div>
  <div id="sel-info" style="display:none; margin-top:4px; border-top:1px solid #1a2030; padding-top:4px;">
    <div class="selected-name" id="sel-name">--</div>
    <div><span class="label">POS     </span><span class="value" id="sel-pos">--</span></div>
    <div><span class="label">ROT     </span><span class="value" id="sel-rot">--</span></div>
    <div><span class="label">SIZE    </span><span class="value" id="sel-scale">--</span></div>
    <div><span class="label">LAYER   </span><span class="value" id="sel-layer">Layer 0</span></div>
  </div>
</div>

<!-- Status bar -->
<div id="status-bar">
  <div class="status-cell" id="sb-mode">MODE: NAVIGATE</div>
  <div class="status-cell" id="sb-snap">SNAP: OFF</div>
  <div class="status-cell" id="sb-wire">WIRE: OFF</div>
  <div class="status-cell" id="sb-layer">LAYER: Layer 0</div>
  <div class="status-cell" id="sb-msg" style="flex:1;">Ready — add shapes from sidebar · [X] AI analyze · [F] Frame selection</div>
  <div class="status-cell" id="sb-dist" style="min-width:140px; text-align:right;"></div>
</div>

<!-- Properties panel -->
<div id="props-panel">
  <div id="props-header">
    <span>Properties</span>
    <span id="props-type" style="color:#2a5a82;font-size:9px;"></span>
  </div>
  <div id="props-body"></div>
</div>

<!-- Measurement display -->
<div id="measure-panel">
  <span id="measure-text">Click two points to measure</span>
</div>

<!-- Section plane -->
<div id="section-indicator"></div>

<!-- Snap dot -->
<div id="snap-dot"></div>

<!-- AI Panel -->
<div id="ai-panel">
  <div id="ai-header">
    <span>📐 Claude Analysis</span>
    <button id="ai-close" onclick="closeAI()">✕</button>
  </div>
  <div id="ai-body">
    <div class="loading-row">
      <span>Initializing</span>
      <span class="dot">■</span><span class="dot">■</span><span class="dot">■</span>
    </div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ── Config from Python ────────────────────────────────────────
const OPENROUTER_API_KEY  = "{OPENROUTER_API_KEY}";
const OPENROUTER_MODEL    = "{OPENROUTER_MODEL}";
const ANALYSIS_MODE       = "{analysis_mode}";
const AI_DETAIL           = "{detail_js}";
let   transformMode       = "{mode_js}";
let   transformSpace      = "{space_js}";

// ── Renderer ──────────────────────────────────────────────────
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.setSize(innerWidth, innerHeight);
document.body.appendChild(renderer.domElement);

function onResize() {{
  renderer.setSize(innerWidth, innerHeight);
  cam.aspect = innerWidth / innerHeight;
  cam.updateProjectionMatrix();
}}
window.addEventListener('resize', onResize);

// ── Scene ─────────────────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0e14);
scene.fog = new THREE.FogExp2(0x0a0e14, 0.010);

// ── Camera ────────────────────────────────────────────────────
const cam = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.05, 1000);
const orb = {{ theta:0.65, phi:1.05, r:18, tx:0, ty:0.5, tz:0 }};
function applyOrbit() {{
  const sp = Math.sin(orb.phi), cp = Math.cos(orb.phi);
  const st = Math.sin(orb.theta), ct = Math.cos(orb.theta);
  cam.position.set(orb.tx + orb.r*sp*st, orb.ty + orb.r*cp, orb.tz + orb.r*sp*ct);
  cam.lookAt(orb.tx, orb.ty, orb.tz);
}}

// ── Lights ────────────────────────────────────────────────────
const ambient = new THREE.AmbientLight(0x1a2a3a, 0.8);
scene.add(ambient);

const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
keyLight.position.set(14, 22, 10);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(4096, 4096);
keyLight.shadow.camera.left = -30; keyLight.shadow.camera.right = 30;
keyLight.shadow.camera.top  =  30; keyLight.shadow.camera.bottom = -30;
keyLight.shadow.bias = -0.0002;
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0x203060, 0.5);
fillLight.position.set(-10, 6, -8);
scene.add(fillLight);

const rimLight = new THREE.DirectionalLight(0x102040, 0.3);
rimLight.position.set(0, -5, -12);
scene.add(rimLight);

// ── Ground plane (receives shadows) ──────────────────────────
const groundGeo = new THREE.PlaneGeometry(200, 200);
const groundMat = new THREE.MeshStandardMaterial({{ color:0x0a0f16, roughness:0.95, metalness:0.05 }});
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI/2;
ground.receiveShadow = true;
ground.name = '_ground';
scene.add(ground);

// ── Grid system ───────────────────────────────────────────────
const gridMajor = new THREE.GridHelper(40, 8, 0x1e2d3d, 0x121a24);
const gridMinor = new THREE.GridHelper(40, 40, 0x0e181f, 0x0c151c);
gridMajor.position.y = 0.001;
gridMinor.position.y = 0.002;
scene.add(gridMajor);
scene.add(gridMinor);

// ── World origin axes ─────────────────────────────────────────
let originAxesGroup = null;
function buildOriginAxes() {{
  if(originAxesGroup) {{ scene.remove(originAxesGroup); originAxesGroup=null; }}
  if(!cadState.showOriginAxes) return;
  originAxesGroup = new THREE.Group();
  const axDefs = [
    {{ dir:[1,0,0], color:0xff3333, lbl:'X' }},
    {{ dir:[0,1,0], color:0x33ff33, lbl:'Y' }},
    {{ dir:[0,0,1], color:0x3366ff, lbl:'Z' }},
  ];
  axDefs.forEach(ax => {{
    const mat  = new THREE.LineBasicMaterial({{ color:ax.color, depthTest:false }});
    const pts  = [new THREE.Vector3(0,0,0), new THREE.Vector3(...ax.dir).multiplyScalar(5)];
    const geo  = new THREE.BufferGeometry().setFromPoints(pts);
    const line = new THREE.Line(geo, mat);
    line.renderOrder = 10;
    originAxesGroup.add(line);
    const tick = new THREE.Mesh(
      new THREE.ConeGeometry(0.06,0.25,8),
      new THREE.MeshBasicMaterial({{ color:ax.color, depthTest:false }})
    );
    tick.position.set(...ax.dir.map(v=>v*5));
    tick.lookAt(new THREE.Vector3(...ax.dir.map(v=>v*10)));
    tick.renderOrder = 10;
    originAxesGroup.add(tick);
  }});
  scene.add(originAxesGroup);
}}

// ── CAD State ─────────────────────────────────────────────────
const cadState = {{
  snapGrid: false,
  snapSize: 0.25,
  wireframe: false,
  showBbox: false,
  showDimensions: false,
  showNormals: false,
  showOriginAxes: false,
  measureMode: false,
  sectionMode: false,
  sectionY: 0,
  activeLayer: 'Layer 0',
  layers: {{
    'Layer 0':     {{ visible:true, locked:false, color:0x4a9eff }},
    'Construction':{{ visible:true, locked:false, color:0x808040 }},
    'Hidden':      {{ visible:false,locked:false, color:0x808080 }},
    'Dimensions':  {{ visible:true, locked:false, color:0x40a0a0 }},
    'Section':     {{ visible:true, locked:false, color:0xff6040 }},
  }},
  measurePoints: [],
  measureLine: null,
}};

// ── Object state ──────────────────────────────────────────────
let objects = [], selected = null;
const nameCnt = {{}};
const COLORS = [0x4a9eff,0xff6b6b,0x6bff8b,0xffd93d,0xa78bfa,0xfb923c,0x34d399,0xf472b6,0x60c0e0,0xff8040];
let colorIdx = 0;

// per-object data: {{mesh, bboxHelper, normalHelpers, dimGroup, layer}}
const objectData = new Map();

// ── Geometry factories ────────────────────────────────────────
const GEOS = {{
  box:      () => new THREE.BoxGeometry(1.5, 1.5, 1.5),
  sphere:   () => new THREE.SphereGeometry(0.9, 48, 48),
  cylinder: () => new THREE.CylinderGeometry(0.7, 0.7, 2.0, 48),
  cone:     () => new THREE.ConeGeometry(0.8, 2.0, 48),
  torus:    () => new THREE.TorusGeometry(0.8, 0.26, 20, 80),
  plane:    () => new THREE.PlaneGeometry(2.5, 2.5, 4, 4),
  wedge:    () => {{
    const g = new THREE.BufferGeometry();
    const v = new Float32Array([
      -0.75,0,-0.75,  0.75,0,-0.75,  0.75,0,0.75,
      -0.75,0,0.75,   -0.75,1.5,-0.75, 0.75,1.5,-0.75,
    ]);
    const i = new Uint16Array([
      0,1,2, 0,2,3,   // bottom
      4,5,1, 4,1,0,   // back
      0,3,4,           // left
      1,5,2,           // right
      3,2,5, 3,5,4,   // front
    ]);
    g.setAttribute('position', new THREE.BufferAttribute(v, 3));
    g.setIndex(new THREE.BufferAttribute(i, 1));
    g.computeVertexNormals();
    return g;
  }},
  pipe:     () => new THREE.TorusGeometry(0.7, 0.12, 12, 64),
}};

// ── Material factory ─────────────────────────────────────────
function makeMat(color, rough=0.38, metal=0.18) {{
  return new THREE.MeshStandardMaterial({{
    color, roughness:rough, metalness:metal,
    envMapIntensity: 0.4,
  }});
}}

// ── Bbox helper ───────────────────────────────────────────────
function buildBbox(mesh) {{
  const helper = new THREE.BoxHelper(mesh, 0x406080);
  helper.material.linewidth = 1;
  helper.name = '_bbox';
  scene.add(helper);
  return helper;
}}

// ── Dimension lines for selected object ──────────────────────
function buildDimGroup(mesh) {{
  const g = new THREE.Group(); g.name='_dim';
  const bb = new THREE.Box3().setFromObject(mesh);
  const sz = new THREE.Vector3(); bb.getSize(sz);
  const ctr = new THREE.Vector3(); bb.getCenter(ctr);

  const lineMat = new THREE.LineBasicMaterial({{ color:0x40a0a0, depthTest:false }});
  const textColor = '#40a0a0';

  function addDimLine(from, to) {{
    const pts = [from.clone(), to.clone()];
    const geo = new THREE.BufferGeometry().setFromPoints(pts);
    const line = new THREE.Line(geo, lineMat);
    line.renderOrder = 5;
    g.add(line);
  }}

  // X dimension
  const xFrom = new THREE.Vector3(bb.min.x, bb.min.y-0.3, ctr.z);
  const xTo   = new THREE.Vector3(bb.max.x, bb.min.y-0.3, ctr.z);
  addDimLine(xFrom, xTo);
  addDimLine(new THREE.Vector3(bb.min.x, bb.min.y, ctr.z), xFrom);
  addDimLine(new THREE.Vector3(bb.max.x, bb.min.y, ctr.z), xTo);

  // Y dimension
  const yFrom = new THREE.Vector3(bb.max.x+0.3, bb.min.y, ctr.z);
  const yTo   = new THREE.Vector3(bb.max.x+0.3, bb.max.y, ctr.z);
  addDimLine(yFrom, yTo);
  addDimLine(new THREE.Vector3(bb.max.x, bb.min.y, ctr.z), yFrom);
  addDimLine(new THREE.Vector3(bb.max.x, bb.max.y, ctr.z), yTo);

  // Z dimension
  const zFrom = new THREE.Vector3(ctr.x, bb.min.y-0.3, bb.min.z);
  const zTo   = new THREE.Vector3(ctr.x, bb.min.y-0.3, bb.max.z);
  addDimLine(zFrom, zTo);
  addDimLine(new THREE.Vector3(ctr.x, bb.min.y, bb.min.z), zFrom);
  addDimLine(new THREE.Vector3(ctr.x, bb.min.y, bb.max.z), zTo);

  scene.add(g);
  return g;
}}

// ── Normal helpers ────────────────────────────────────────────
function buildNormalHelper(mesh) {{
  const helper = new THREE.VertexNormalsHelper(mesh, 0.25, 0x00ff88);
  helper.name = '_normals';
  scene.add(helper);
  return helper;
}}

// ── Add shape ─────────────────────────────────────────────────
function addShape(type) {{
  if(cadState.layers[cadState.activeLayer]?.locked) {{
    setMsg('Layer is locked');
    return;
  }}
  nameCnt[type] = (nameCnt[type]||0)+1;
  const color = COLORS[colorIdx++%COLORS.length];
  const layerDef = cadState.layers[cadState.activeLayer];
  const mat = makeMat(layerDef?.color || color);
  const geo = GEOS[type] ? GEOS[type]() : GEOS.box();
  const mesh = new THREE.Mesh(geo, mat);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  const a = Math.random()*Math.PI*2, r = Math.random()*2.5;
  mesh.position.set(Math.cos(a)*r, 0.8, Math.sin(a)*r);
  mesh.userData = {{ type, name: type+'_'+nameCnt[type], layer: cadState.activeLayer }};
  scene.add(mesh);
  objects.push(mesh);

  const bbox = cadState.showBbox ? buildBbox(mesh) : null;
  let normalH = null;
  let dimGroup = null;
  objectData.set(mesh, {{ bbox, normalH, dimGroup }});

  if(!cadState.layers[cadState.activeLayer].visible) mesh.visible = false;

  selectObj(mesh);
  setMsg('Added ' + mesh.userData.name + ' on layer [' + cadState.activeLayer + ']');
  updateObjCount();
}}

// ── Duplicate ─────────────────────────────────────────────────
function duplicateSelected() {{
  if(!selected) return setMsg('Nothing selected');
  const src = selected;
  const newMesh = src.clone();
  newMesh.material = src.material.clone();
  newMesh.position.x += 1.8;
  const t = src.userData.type;
  nameCnt[t] = (nameCnt[t]||0)+1;
  newMesh.userData = {{ ...src.userData, name: t+'_'+nameCnt[t] }};
  scene.add(newMesh);
  objects.push(newMesh);
  const bbox = cadState.showBbox ? buildBbox(newMesh) : null;
  objectData.set(newMesh, {{ bbox, normalH:null, dimGroup:null }});
  selectObj(newMesh);
  setMsg('Duplicated → ' + newMesh.userData.name);
  updateObjCount();
}}

// ── Delete ────────────────────────────────────────────────────
function deleteSelected() {{
  if(!selected) return setMsg('Nothing selected');
  const data = objectData.get(selected);
  if(data?.bbox)     scene.remove(data.bbox);
  if(data?.normalH)  scene.remove(data.normalH);
  if(data?.dimGroup) scene.remove(data.dimGroup);
  objectData.delete(selected);
  scene.remove(selected);
  objects = objects.filter(o=>o!==selected);
  if(gizmoGroup) {{ scene.remove(gizmoGroup); gizmoGroup=null; }}
  selected = null;
  updatePropsPanel(null);
  updateCoordHUD();
  setMsg('Deleted');
  updateObjCount();
}}

// ── Clear ─────────────────────────────────────────────────────
function clearScene() {{
  objects.forEach(o => {{
    const d = objectData.get(o);
    if(d?.bbox)     scene.remove(d.bbox);
    if(d?.normalH)  scene.remove(d.normalH);
    if(d?.dimGroup) scene.remove(d.dimGroup);
    scene.remove(o);
  }});
  objects = [];
  objectData.clear();
  colorIdx = 0;
  Object.keys(nameCnt).forEach(k=>delete nameCnt[k]);
  if(gizmoGroup) {{ scene.remove(gizmoGroup); gizmoGroup=null; }}
  selected = null;
  updatePropsPanel(null);
  closeAI();
  setMsg('Scene cleared');
  updateObjCount();
}}

// ── Set material ──────────────────────────────────────────────
function setMaterial(hexStr, rough, metal) {{
  if(!selected) return setMsg('Select an object first');
  selected.material.color.set(hexStr);
  selected.material.roughness = parseFloat(rough);
  selected.material.metalness = parseFloat(metal);
  selected.material.needsUpdate = true;
  updatePropsPanel(selected);
  setMsg('Material updated on ' + selected.userData.name);
}}

// ── Apply position ────────────────────────────────────────────
function applyPosition(x,y,z) {{
  if(!selected) return setMsg('No object selected');
  selected.position.set(parseFloat(x), parseFloat(y), parseFloat(z));
  syncGizmo();
  updateBbox();
  updatePropsPanel(selected);
  setMsg('Position set to (' + x + ', ' + y + ', ' + z + ')');
}}

// ── Gizmo ─────────────────────────────────────────────────────
let gizmoGroup = null;
function buildGizmo() {{
  if(gizmoGroup) scene.remove(gizmoGroup);
  gizmoGroup = new THREE.Group(); gizmoGroup.name='_gizmo';
  if(transformMode === 'move') buildMoveGizmo();
  else if(transformMode === 'rotate') buildRotateGizmo();
  else if(transformMode === 'scale') buildScaleGizmo();
  scene.add(gizmoGroup);
}}

const AX = {{ x:0xff3333, y:0x33ff33, z:0x3366ff }};

function buildMoveGizmo() {{
  ['x','y','z'].forEach(ax => {{
    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.04,1.8,8),
      new THREE.MeshBasicMaterial({{color:AX[ax],depthTest:false}}));
    const tip = new THREE.Mesh(new THREE.ConeGeometry(0.11,0.32,8),
      new THREE.MeshBasicMaterial({{color:AX[ax],depthTest:false}}));
    tip.position.y = 1.06;
    const arr = new THREE.Group(); arr.add(shaft,tip); arr.userData.axis=ax;
    if(ax==='x') {{ arr.rotation.z=-Math.PI/2; arr.position.x=1.0; }}
    else if(ax==='y') {{ arr.position.y=1.0; }}
    else {{ arr.rotation.x=Math.PI/2; arr.position.z=1.0; }}
    gizmoGroup.add(arr);
  }});
  // Plane handles
  [['x','z',0xffff33],['x','y',0x33ffff],['y','z',0xff33ff]].forEach(([a,b,c]) => {{
    const sq = new THREE.Mesh(new THREE.PlaneGeometry(0.4,0.4),
      new THREE.MeshBasicMaterial({{color:c,transparent:true,opacity:0.25,side:THREE.DoubleSide,depthTest:false}}));
    sq.userData.axis = a+b;
    if(a==='x'&&b==='z') {{ sq.rotation.x=-Math.PI/2; sq.position.set(0.5,0,0.5); }}
    else if(a==='x'&&b==='y') {{ sq.position.set(0.5,0.5,0); }}
    else {{ sq.rotation.y=Math.PI/2; sq.position.set(0,0.5,0.5); }}
    gizmoGroup.add(sq);
  }});
}}

function buildRotateGizmo() {{
  [['x',0xff3333],['y',0x33ff33],['z',0x3366ff]].forEach(([ax,col]) => {{
    const geo = new THREE.TorusGeometry(1.1, 0.04, 8, 64);
    const ring = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({{color:col,depthTest:false}}));
    ring.userData.axis = ax;
    if(ax==='x') ring.rotation.y = Math.PI/2;
    else if(ax==='z') ring.rotation.x = Math.PI/2;
    gizmoGroup.add(ring);
  }});
}}

function buildScaleGizmo() {{
  ['x','y','z'].forEach(ax => {{
    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.04,1.8,8),
      new THREE.MeshBasicMaterial({{color:AX[ax],depthTest:false}}));
    const cube = new THREE.Mesh(new THREE.BoxGeometry(0.2,0.2,0.2),
      new THREE.MeshBasicMaterial({{color:AX[ax],depthTest:false}}));
    cube.position.y = 1.1;
    const arr = new THREE.Group(); arr.add(shaft,cube); arr.userData.axis=ax;
    if(ax==='x') {{ arr.rotation.z=-Math.PI/2; arr.position.x=1.0; }}
    else if(ax==='y') {{ arr.position.y=1.0; }}
    else {{ arr.rotation.x=Math.PI/2; arr.position.z=1.0; }}
    gizmoGroup.add(arr);
  }});
  // Uniform scale
  const uni = new THREE.Mesh(new THREE.SphereGeometry(0.14,8,8),
    new THREE.MeshBasicMaterial({{color:0xffffff,depthTest:false}}));
  uni.userData.axis='xyz'; gizmoGroup.add(uni);
}}

function syncGizmo() {{
  if(!selected||!gizmoGroup) return;
  gizmoGroup.position.copy(selected.position);
  const bb = new THREE.Box3().setFromObject(selected);
  const sz = new THREE.Vector3(); bb.getSize(sz);
  const sc = Math.max(sz.x,sz.y,sz.z)*0.45+0.5;
  gizmoGroup.scale.setScalar(sc);
  if(transformSpace==='local') {{
    gizmoGroup.rotation.copy(selected.rotation);
  }} else {{
    gizmoGroup.rotation.set(0,0,0);
  }}
}}

// ── Bbox update ───────────────────────────────────────────────
function updateBbox() {{
  objectData.forEach((d, mesh) => {{
    if(d.bbox) d.bbox.update();
  }});
}}

// ── Properties panel ──────────────────────────────────────────
function updatePropsPanel(mesh) {{
  const panel = document.getElementById('props-panel');
  if(!mesh) {{ panel.style.display='none'; return; }}
  panel.style.display='block';
  document.getElementById('props-type').textContent = mesh.userData.type?.toUpperCase();
  const bb = new THREE.Box3().setFromObject(mesh);
  const sz = new THREE.Vector3(); bb.getSize(sz);
  const p = mesh.position, r = mesh.rotation, s = mesh.scale;
  const col = '#'+mesh.material.color.getHexString();
  document.getElementById('props-body').innerHTML = `
    <div class="prop-section">Location</div>
    <div class="prop-row"><span class="prop-label">X</span><span class="prop-val">${{p.x.toFixed(3)}}</span></div>
    <div class="prop-row"><span class="prop-label">Y</span><span class="prop-val">${{p.y.toFixed(3)}}</span></div>
    <div class="prop-row"><span class="prop-label">Z</span><span class="prop-val">${{p.z.toFixed(3)}}</span></div>
    <div class="prop-section">Rotation (rad)</div>
    <div class="prop-row"><span class="prop-label">Rx</span><span class="prop-val">${{r.x.toFixed(3)}}</span></div>
    <div class="prop-row"><span class="prop-label">Ry</span><span class="prop-val">${{r.y.toFixed(3)}}</span></div>
    <div class="prop-row"><span class="prop-label">Rz</span><span class="prop-val">${{r.z.toFixed(3)}}</span></div>
    <div class="prop-section">Bounding Box</div>
    <div class="prop-row"><span class="prop-label">Width</span><span class="prop-val">${{sz.x.toFixed(3)}}</span></div>
    <div class="prop-row"><span class="prop-label">Height</span><span class="prop-val">${{sz.y.toFixed(3)}}</span></div>
    <div class="prop-row"><span class="prop-label">Depth</span><span class="prop-val">${{sz.z.toFixed(3)}}</span></div>
    <div class="prop-section">Material</div>
    <div class="prop-row"><span class="prop-label">Color</span><span class="prop-val">${{col}}</span></div>
    <div class="prop-row"><span class="prop-label">Rough</span><span class="prop-val">${{mesh.material.roughness?.toFixed(2)||'--'}}</span></div>
    <div class="prop-row"><span class="prop-label">Metal</span><span class="prop-val">${{mesh.material.metalness?.toFixed(2)||'--'}}</span></div>
    <div class="prop-section">CAD Info</div>
    <div class="prop-row"><span class="prop-label">Layer</span><span class="prop-val">${{mesh.userData.layer||'Layer 0'}}</span></div>
    <div class="prop-row"><span class="prop-label">Volume</span><span class="prop-val">≈${{(sz.x*sz.y*sz.z).toFixed(3)}} u³</span></div>
  `;
}}

// ── Coordinate HUD ────────────────────────────────────────────
function updateCoordHUD() {{
  const p = cam.position;
  document.getElementById('cam-pos').textContent =
    `${{p.x.toFixed(2)}}, ${{p.y.toFixed(2)}}, ${{p.z.toFixed(2)}}`;
  if(selected) {{
    const sp = selected.position;
    const sr = selected.rotation;
    const bb = new THREE.Box3().setFromObject(selected);
    const sz = new THREE.Vector3(); bb.getSize(sz);
    document.getElementById('sel-info').style.display='block';
    document.getElementById('sel-name').textContent  = selected.userData.name;
    document.getElementById('sel-pos').textContent   = `${{sp.x.toFixed(2)}}, ${{sp.y.toFixed(2)}}, ${{sp.z.toFixed(2)}}`;
    document.getElementById('sel-rot').textContent   = `${{(sr.x*180/Math.PI).toFixed(1)}}°, ${{(sr.y*180/Math.PI).toFixed(1)}}°, ${{(sr.z*180/Math.PI).toFixed(1)}}°`;
    document.getElementById('sel-scale').textContent = `${{sz.x.toFixed(2)}} × ${{sz.y.toFixed(2)}} × ${{sz.z.toFixed(2)}}`;
    document.getElementById('sel-layer').textContent = selected.userData.layer||'Layer 0';
  }} else {{
    document.getElementById('sel-info').style.display='none';
  }}
}}

function updateObjCount() {{
  document.getElementById('obj-count').textContent = objects.length;
}}

// ── Select object ─────────────────────────────────────────────
function selectObj(obj) {{
  if(selected && selected!==obj) {{
    selected.material.emissive.setHex(0x000000);
    // Remove per-selection dim group
    const d = objectData.get(selected);
    if(d?.dimGroup) {{ scene.remove(d.dimGroup); d.dimGroup=null; }}
    if(d?.normalH && !cadState.showNormals) {{ scene.remove(d.normalH); d.normalH=null; }}
  }}
  selected = obj;
  if(selected) {{
    selected.material.emissive.setHex(0x102840);
    buildGizmo(); syncGizmo();
    if(cadState.showDimensions) {{
      const d = objectData.get(selected);
      if(d && !d.dimGroup) {{ d.dimGroup = buildDimGroup(selected); }}
    }}
    if(cadState.showNormals) {{
      try {{
        const d = objectData.get(selected);
        if(d && !d.normalH) {{ d.normalH = buildNormalHelper(selected); }}
      }} catch(e) {{}}
    }}
    updatePropsPanel(selected);
    updateCoordHUD();
    setMsg('[' + selected.userData.name + '] selected on layer [' + (selected.userData.layer||'Layer 0') + '] · X=analyze · F=frame');
    document.getElementById('sb-layer').textContent = 'LAYER: ' + (selected.userData.layer||'Layer 0');
  }} else {{
    if(gizmoGroup) {{ scene.remove(gizmoGroup); gizmoGroup=null; }}
    updatePropsPanel(null);
    updateCoordHUD();
  }}
}}

// ── Toggle CAD features ───────────────────────────────────────
function toggleSnapGrid() {{
  cadState.snapGrid = !cadState.snapGrid;
  document.getElementById('sb-snap').textContent = 'SNAP: ' + (cadState.snapGrid ? cadState.snapSize : 'OFF');
  document.getElementById('sb-snap').className = 'status-cell' + (cadState.snapGrid?' active':'');
  setMsg('Snap grid ' + (cadState.snapGrid?'ON ('+cadState.snapSize+' units)':'OFF'));
}}

function toggleWireframe() {{
  cadState.wireframe = !cadState.wireframe;
  objects.forEach(o => {{
    o.material.wireframe = cadState.wireframe;
  }});
  document.getElementById('sb-wire').textContent = 'WIRE: ' + (cadState.wireframe?'ON':'OFF');
  document.getElementById('sb-wire').className = 'status-cell' + (cadState.wireframe?' active':'');
  setMsg('Wireframe ' + (cadState.wireframe?'ON':'OFF'));
}}

function toggleBbox() {{
  cadState.showBbox = !cadState.showBbox;
  objects.forEach(o => {{
    const d = objectData.get(o);
    if(cadState.showBbox) {{
      if(d && !d.bbox) d.bbox = buildBbox(o);
    }} else {{
      if(d?.bbox) {{ scene.remove(d.bbox); d.bbox=null; }}
    }}
  }});
  setMsg('Bounding boxes ' + (cadState.showBbox?'ON':'OFF'));
}}

function toggleDimensions() {{
  cadState.showDimensions = !cadState.showDimensions;
  if(cadState.showDimensions && selected) {{
    const d = objectData.get(selected);
    if(d && !d.dimGroup) d.dimGroup = buildDimGroup(selected);
  }} else {{
    objectData.forEach((d) => {{
      if(d.dimGroup) {{ scene.remove(d.dimGroup); d.dimGroup=null; }}
    }});
  }}
  setMsg('Dimension lines ' + (cadState.showDimensions?'ON':'OFF'));
}}

function toggleNormals() {{
  cadState.showNormals = !cadState.showNormals;
  if(!cadState.showNormals) {{
    objectData.forEach((d) => {{
      if(d.normalH) {{ scene.remove(d.normalH); d.normalH=null; }}
    }});
  }} else if(selected) {{
    try {{
      const d = objectData.get(selected);
      if(d && !d.normalH) d.normalH = buildNormalHelper(selected);
    }} catch(e) {{ setMsg('Normals not available for this geometry'); cadState.showNormals=false; return; }}
  }}
  setMsg('Normal display ' + (cadState.showNormals?'ON (selected object)':'OFF'));
}}

function toggleOriginAxes() {{
  cadState.showOriginAxes = !cadState.showOriginAxes;
  buildOriginAxes();
  setMsg('Origin axes ' + (cadState.showOriginAxes?'ON':'OFF'));
}}

function toggleMeasureMode() {{
  cadState.measureMode = !cadState.measureMode;
  cadState.measurePoints = [];
  if(cadState.measureLine) {{ scene.remove(cadState.measureLine); cadState.measureLine=null; }}
  const mp = document.getElementById('measure-panel');
  mp.style.display = cadState.measureMode ? 'block' : 'none';
  if(cadState.measureMode) {{
    document.getElementById('measure-text').textContent = 'Click 1st point on any surface';
    setMsg('Measure mode ON — click two points on objects or ground');
    document.getElementById('sb-mode').textContent = 'MODE: MEASURE';
    document.getElementById('sb-mode').className = 'status-cell active';
  }} else {{
    setMsg('Measure mode OFF');
    document.getElementById('sb-mode').textContent = 'MODE: ' + transformMode.toUpperCase();
    document.getElementById('sb-mode').className = 'status-cell';
  }}
}}

function toggleSection() {{
  cadState.sectionMode = !cadState.sectionMode;
  if(cadState.sectionMode) {{
    document.getElementById('section-indicator').style.display='block';
    objects.forEach(o => {{
      o.material.clippingPlanes = [new THREE.Plane(new THREE.Vector3(0,-1,0), cadState.sectionY+2)];
      o.material.clipShadows = true;
    }});
    renderer.localClippingEnabled = true;
    setMsg('Section plane ON at Y=' + cadState.sectionY.toFixed(2) + ' — scroll wheel over center to move');
  }} else {{
    document.getElementById('section-indicator').style.display='none';
    objects.forEach(o => {{ o.material.clippingPlanes = []; }});
    renderer.localClippingEnabled = false;
    setMsg('Section plane OFF');
  }}
}}

function layerVis(layerName) {{
  if(!cadState.layers[layerName]) return;
  cadState.layers[layerName].visible = !cadState.layers[layerName].visible;
  const vis = cadState.layers[layerName].visible;
  objects.forEach(o => {{
    if(o.userData.layer===layerName) o.visible=vis;
  }});
  setMsg('Layer [' + layerName + '] ' + (vis?'visible':'hidden'));
}}

function layerLock(layerName) {{
  if(!cadState.layers[layerName]) return;
  cadState.layers[layerName].locked = !cadState.layers[layerName].locked;
  setMsg('Layer [' + layerName + '] ' + (cadState.layers[layerName].locked?'LOCKED':'unlocked'));
}}

// ── Frame selection ───────────────────────────────────────────
function frameSelected() {{
  const target = selected || null;
  if(!target) {{
    orb.r=18; orb.tx=0; orb.ty=0.5; orb.tz=0;
    setMsg('Framed scene');
    return;
  }}
  const bb = new THREE.Box3().setFromObject(target);
  const ctr = new THREE.Vector3(); bb.getCenter(ctr);
  const sz = new THREE.Vector3(); bb.getSize(sz);
  orb.tx=ctr.x; orb.ty=ctr.y; orb.tz=ctr.z;
  orb.r = Math.max(sz.x,sz.y,sz.z)*2.5+3;
  setMsg('Framed: ' + target.userData.name);
}}

// ── AI Analysis via OpenRouter ────────────────────────────────
function closeAI() {{
  document.getElementById('ai-panel').style.display='none';
}}

async function analyzeSelected() {{
  if(!selected) return setMsg('Select an object first (click it), then press X');
  if(!OPENROUTER_API_KEY) {{
    setMsg('No API key — add OPENROUTER_API_KEY to .streamlit/secrets.toml');
    return;
  }}

  const panel = document.getElementById('ai-panel');
  const body  = document.getElementById('ai-body');
  panel.style.display='flex';
  body.innerHTML = `
    <div class="obj-tag">${{selected.userData.name}} · ${{selected.userData.type}}</div>
    <div class="loading-row"><span>Querying</span>
    <span class="dot">■</span><span class="dot">■</span><span class="dot">■</span></div>`;

  setMsg('Sending to Claude via OpenRouter…');

  const bb = new THREE.Box3().setFromObject(selected);
  const sz = new THREE.Vector3(); bb.getSize(sz);
  const ctr = new THREE.Vector3(); bb.getCenter(ctr);
  const c = selected.material.color;

  const allObjSummary = objects.map(o => {{
    const ob = new THREE.Box3().setFromObject(o);
    const os = new THREE.Vector3(); ob.getSize(os);
    return `${{o.userData.name}} (${{o.userData.type}}) at (${{o.position.x.toFixed(2)}},${{o.position.y.toFixed(2)}},${{o.position.z.toFixed(2)}}) size ${{os.x.toFixed(2)}}×${{os.y.toFixed(2)}}×${{os.z.toFixed(2)}} layer=${{o.userData.layer||'Layer 0'}}`;
  }}).join('\\n  ');

  const modePrompts = {{
    "General Design Review":       "Give a concise engineering design review covering geometry, placement, proportions, and role in the assembly. Use clear engineering vocabulary.",
    "Structural Analysis":         "Analyze from a structural engineering standpoint: stress concentrations, weak points, support conditions, load paths, and recommended improvements.",
    "Dimensional Check":           "Review the dimensional proportions of this object. Flag anything that looks non-standard for real-world applications. Suggest standard sizes or ratios.",
    "GD&T Suggestions":            "Suggest appropriate GD&T (Geometric Dimensioning and Tolerancing) annotations for this feature. Include datum references, form tolerances, and position tolerances where applicable.",
    "Aesthetic & Composition":     "Evaluate the aesthetic and visual composition relative to the other objects in the scene.",
    "Manufacturing Feasibility":   "Assess manufacturability: draft angles, parting lines, undercuts, minimum wall thickness, and machining access. Note which processes (casting, milling, 3D printing) are most suitable.",
    "FEA Pre-check":               "Identify regions that would need mesh refinement in FEA: fillets, holes, transitions, thin walls. Recommend element types and boundary condition locations.",
    "Assembly Notes":              "Describe how this part likely interfaces with other objects in the scene. Suggest mate types, clearance fits, and assembly sequence.",
  }};

  const detailInstr = AI_DETAIL==='detailed'
    ? 'Provide a thorough technical response with sub-sections for each major concern (3-6 paragraphs).'
    : 'Be concise — 2-4 short paragraphs with key engineering points only.';

  const prompt = `You are a senior mechanical engineer and CAD specialist doing a technical review.

SELECTED OBJECT:
  Name:           ${{selected.userData.name}}
  Type:           ${{selected.userData.type}}
  Layer:          ${{selected.userData.layer||'Layer 0'}}
  Position:       X=${{selected.position.x.toFixed(3)}}, Y=${{selected.position.y.toFixed(3)}}, Z=${{selected.position.z.toFixed(3)}}
  Rotation (rad): Rx=${{selected.rotation.x.toFixed(3)}}, Ry=${{selected.rotation.y.toFixed(3)}}, Rz=${{selected.rotation.z.toFixed(3)}}
  Bounding Box:   W=${{sz.x.toFixed(3)}} × H=${{sz.y.toFixed(3)}} × D=${{sz.z.toFixed(3)}} (units)
  Centroid:       (${{ctr.x.toFixed(3)}}, ${{ctr.y.toFixed(3)}}, ${{ctr.z.toFixed(3)}})
  Volume (bbox):  ${{(sz.x*sz.y*sz.z).toFixed(4)}} cubic units
  Color:          #${{c.getHexString()}}
  Roughness:      ${{selected.material.roughness?.toFixed(2)||'0.38'}}
  Metalness:      ${{selected.material.metalness?.toFixed(2)||'0.18'}}

OTHER OBJECTS IN SCENE (${{objects.length}} total):
  ${{allObjSummary}}

ANALYSIS TASK: ${{modePrompts[ANALYSIS_MODE]||modePrompts["General Design Review"]}}

${{detailInstr}}
Reference the actual object name and specific numerical properties in your response.`;

  try {{
    const resp = await fetch("https://openrouter.ai/api/v1/chat/completions", {{
      method:"POST",
      headers:{{
        "Authorization": "Bearer " + OPENROUTER_API_KEY,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ai-cad-studio.streamlit.app",
        "X-Title": "AI CAD Studio",
      }},
      body: JSON.stringify({{
        model: OPENROUTER_MODEL,
        max_tokens: AI_DETAIL==='detailed' ? 900 : 500,
        messages:[{{ role:"user", content:prompt }}],
        temperature: 0.3,
      }}),
    }});

    const data = await resp.json();

    if(!resp.ok) {{
      const errMsg = data.error?.message || resp.statusText;
      body.innerHTML = `
        <div class="obj-tag">${{selected.userData.name}}</div>
        <div style="color:#e05555;font-size:11px;">
          ✗ API Error ${{resp.status}}: ${{errMsg}}
          ${{resp.status===401 ? '<br><br>Check OPENROUTER_API_KEY in secrets.toml' : ''}}
          ${{resp.status===404 ? '<br><br>Model not found: ' + OPENROUTER_MODEL : ''}}
        </div>`;
      return setMsg('API error ${{resp.status}} — check the panel');
    }}

    const text = data.choices?.[0]?.message?.content || '(no response)';

    const formatted = text.split('\\n').filter(l=>l.trim()).map(l => {{
      if(l.match(/^#+\\s/)) return `<div class="ai-section-head">${{l.replace(/^#+\\s/,'')}}</div>`;
      if(l.match(/^\\*\\*(.+)\\*\\*/)) return `<div class="ai-section-head">${{l.replace(/\\*\\*/g,'')}}</div>`;
      return `<p style="margin-bottom:9px;">${{l}}</p>`;
    }}).join('');

    body.innerHTML = `
      <div class="obj-tag">${{selected.userData.name}} · ${{selected.userData.type}} · ${{ANALYSIS_MODE}}</div>
      ${{formatted}}
      <div style="margin-top:12px;padding-top:8px;border-top:1px solid #1a2030;
        font-size:9px;color:#2a4060;">
        Model: ${{OPENROUTER_MODEL}} · Mode: ${{AI_DETAIL}}
      </div>`;

    setMsg('Analysis complete for ' + selected.userData.name);

  }} catch(err) {{
    body.innerHTML = `
      <div class="obj-tag">${{selected.userData.name}}</div>
      <div style="color:#e05555;font-size:11px;">
        ✗ Network error: ${{err.message}}<br><br>
        Check your connection and OpenRouter API access.
      </div>`;
    setMsg('Network error');
    console.error(err);
  }}
}}

// ── Measurement tool ──────────────────────────────────────────
const ray = new THREE.Raycaster();
const mouseVec = new THREE.Vector2();

function doMeasureClick(ev) {{
  const rc = renderer.domElement.getBoundingClientRect();
  mouseVec.x = ((ev.clientX-rc.left)/rc.width)*2-1;
  mouseVec.y = -((ev.clientY-rc.top)/rc.height)*2+1;
  ray.setFromCamera(mouseVec, cam);

  const targets = [...objects, ground];
  const hits = ray.intersectObjects(targets, false);
  if(!hits.length) return;

  const pt = hits[0].point.clone();
  if(cadState.snapGrid) {{
    pt.x = Math.round(pt.x/cadState.snapSize)*cadState.snapSize;
    pt.z = Math.round(pt.z/cadState.snapSize)*cadState.snapSize;
  }}

  cadState.measurePoints.push(pt);

  if(cadState.measurePoints.length===1) {{
    document.getElementById('measure-text').textContent =
      'P1=(' + pt.x.toFixed(2) + ', ' + pt.y.toFixed(2) + ', ' + pt.z.toFixed(2) + ') — click 2nd point';
    setMsg('Measure P1 set — click second point');
  }}

  if(cadState.measurePoints.length===2) {{
    const [p1,p2] = cadState.measurePoints;
    const dist = p1.distanceTo(p2);
    const dx = Math.abs(p2.x-p1.x), dy = Math.abs(p2.y-p1.y), dz = Math.abs(p2.z-p1.z);

    if(cadState.measureLine) scene.remove(cadState.measureLine);
    const geo = new THREE.BufferGeometry().setFromPoints([p1,p2]);
    const mat = new THREE.LineDashedMaterial({{color:0x40e0f0,dashSize:0.15,gapSize:0.08,depthTest:false}});
    cadState.measureLine = new THREE.Line(geo, mat);
    cadState.measureLine.computeLineDistances();
    scene.add(cadState.measureLine);

    document.getElementById('measure-text').textContent =
      `Δ=${{dist.toFixed(4)}} | X=${{dx.toFixed(3)}} Y=${{dy.toFixed(3)}} Z=${{dz.toFixed(3)}}`;
    document.getElementById('sb-dist').textContent = `DIST: ${{dist.toFixed(4)}}u`;

    cadState.measurePoints = [];
    setMsg(`Measurement: ${{dist.toFixed(4)}} units — click to measure again`);
  }}
}}

// ── Keyboard shortcuts ────────────────────────────────────────
document.addEventListener('keydown', e => {{
  if(e.target.tagName==='INPUT') return;
  const k = e.key.toLowerCase();
  if(k==='x' && !e.ctrlKey && !e.metaKey) {{ analyzeSelected(); }}
  if(k==='escape') {{ closeAI(); selectObj(null); }}
  if(k==='delete' || k==='backspace') {{ e.preventDefault(); deleteSelected(); }}
  if(k==='d' && !e.ctrlKey) {{ duplicateSelected(); }}
  if(k==='f') {{ frameSelected(); }}
  if(k==='g') {{ toggleSnapGrid(); }}
  if(k==='w') {{ toggleWireframe(); }}
  if(k==='m') {{ toggleMeasureMode(); }}
}});

// ── Mouse / pointer handling ──────────────────────────────────
let isOrb=false, isPan=false, isDrag=false;
let lm={{x:0,y:0}}, dm={{x:0,y:0}};
let dragAxis=null, sp=null, sr=null, ss=null;
let pointerMoved = false;

renderer.domElement.addEventListener('mousedown', e => {{
  dm={{x:e.clientX,y:e.clientY}};
  pointerMoved = false;

  if(selected && gizmoGroup && !cadState.measureMode) {{
    const all=[]; gizmoGroup.traverse(c=>{{if(c.isMesh||c.isLine)all.push(c);}});
    const hits = getHits(e, all);
    if(hits.length>0) {{
      let anc=hits[0].object;
      while(anc.parent && !anc.userData.axis) anc=anc.parent;
      if(anc.userData.axis) {{
        dragAxis=anc.userData.axis; isDrag=true;
        sp=selected.position.clone(); sr=selected.rotation.clone(); ss=selected.scale.clone();
        lm={{x:e.clientX,y:e.clientY}}; return;
      }}
    }}
  }}
  if(e.button===0) isOrb=true;
  if(e.button===2) isPan=true;
  lm={{x:e.clientX,y:e.clientY}};
}});

renderer.domElement.addEventListener('mouseup', e => {{
  if(isDrag) {{ isDrag=false; dragAxis=null; updateBbox(); updatePropsPanel(selected); return; }}
  isOrb=false; isPan=false;
  if(!pointerMoved && Math.abs(e.clientX-dm.x)<6 && Math.abs(e.clientY-dm.y)<6 && e.button===0) {{
    if(cadState.measureMode) {{ doMeasureClick(e); return; }}
    const hits = getHits(e, objects);
    selectObj(hits.length ? hits[0].object : null);
  }}
}});

renderer.domElement.addEventListener('mousemove', e => {{
  if(Math.abs(e.clientX-dm.x)>4||Math.abs(e.clientY-dm.y)>4) pointerMoved=true;

  // Cursor world position
  const hits = getHits(e, [...objects, ground]);
  if(hits.length) {{
    const hp = hits[0].point;
    let cx=hp.x, cy=hp.y, cz=hp.z;
    if(cadState.snapGrid) {{
      cx=Math.round(cx/cadState.snapSize)*cadState.snapSize;
      cz=Math.round(cz/cadState.snapSize)*cadState.snapSize;
      const snapDot = document.getElementById('snap-dot');
      snapDot.style.display='block';
      snapDot.style.left=e.clientX+'px';
      snapDot.style.top =e.clientY+'px';
    }} else {{
      document.getElementById('snap-dot').style.display='none';
    }}
    document.getElementById('cursor-pos').textContent =
      cx.toFixed(2)+', '+cy.toFixed(2)+', '+cz.toFixed(2);
  }}

  if(isDrag && selected && dragAxis) {{
    const dx=(e.clientX-lm.x)*0.018, dy=-(e.clientY-lm.y)*0.018;
    const d=Math.abs(dx)>Math.abs(dy)?dx:dy;
    const ap=dragAxis;

    if(transformMode==='move') {{
      const np=sp.clone();
      const snap = cadState.snapGrid ? cadState.snapSize : null;
      const mv=(v)=>snap ? Math.round(v/snap)*snap : v;
      if(ap==='x')  np.x=mv(sp.x+dx*2.5);
      else if(ap==='y')  np.y=mv(sp.y+dy*2.5);
      else if(ap==='z')  np.z=mv(sp.z+dx*2.5);
      else if(ap==='xz') {{ np.x=mv(sp.x+dx*2.5); np.z=mv(sp.z+dx*2.5); }}
      else if(ap==='xy') {{ np.x=mv(sp.x+dx*2.5); np.y=mv(sp.y+dy*2.5); }}
      else if(ap==='yz') {{ np.y=mv(sp.y+dy*2.5); np.z=mv(sp.z+dx*2.5); }}
      selected.position.copy(np);
    }} else if(transformMode==='rotate') {{
      const nr=sr.clone();
      if(ap==='x') nr.x=sr.x+d*2.8;
      else if(ap==='y') nr.y=sr.y+d*2.8;
      else nr.z=sr.z+d*2.8;
      selected.rotation.copy(nr);
    }} else if(transformMode==='scale') {{
      const sc=ss.clone(), f=1+d*1.4;
      if(ap==='xyz') {{ sc.x=Math.max(0.01,ss.x*f); sc.y=Math.max(0.01,ss.y*f); sc.z=Math.max(0.01,ss.z*f); }}
      else if(ap==='x') sc.x=Math.max(0.01,ss.x*f);
      else if(ap==='y') sc.y=Math.max(0.01,ss.y*f);
      else sc.z=Math.max(0.01,ss.z*f);
      selected.scale.copy(sc);
    }}
    syncGizmo();
    lm={{x:e.clientX,y:e.clientY}};
    updateCoordHUD();
    return;
  }}

  if(isOrb) {{
    orb.theta -= (e.clientX-lm.x)*0.006;
    orb.phi   -= (e.clientY-lm.y)*0.006;
    orb.phi = Math.max(0.05, Math.min(Math.PI-0.05, orb.phi));
  }}
  if(isPan) {{
    const spd=0.010*(orb.r/10);
    const fwd=new THREE.Vector3(orb.tx-cam.position.x, 0, orb.tz-cam.position.z).normalize();
    const right=new THREE.Vector3().crossVectors(fwd, new THREE.Vector3(0,1,0)).normalize();
    orb.tx -= right.x*(e.clientX-lm.x)*spd;
    orb.tz -= right.z*(e.clientX-lm.x)*spd;
    orb.ty += (e.clientY-lm.y)*spd;
  }}
  lm={{x:e.clientX,y:e.clientY}};
}});

renderer.domElement.addEventListener('wheel', e => {{
  if(cadState.sectionMode && e.ctrlKey) {{
    cadState.sectionY += e.deltaY * 0.005;
    objects.forEach(o => {{
      o.material.clippingPlanes = [new THREE.Plane(new THREE.Vector3(0,-1,0), cadState.sectionY+2)];
    }});
    setMsg('Section Y = ' + cadState.sectionY.toFixed(2));
    return;
  }}
  orb.r *= 1 + e.deltaY * 0.0008;
  orb.r = Math.max(1.5, Math.min(200, orb.r));
}}, {{passive:true}});

renderer.domElement.addEventListener('contextmenu', e=>e.preventDefault());

// ── Raycaster helper ──────────────────────────────────────────
function getHits(ev, targets) {{
  const rc = renderer.domElement.getBoundingClientRect();
  mouseVec.x = ((ev.clientX-rc.left)/rc.width)*2-1;
  mouseVec.y = -((ev.clientY-rc.top)/rc.height)*2+1;
  ray.setFromCamera(mouseVec, cam);
  return ray.intersectObjects(targets, true);
}}

// ── Status bar helpers ────────────────────────────────────────
function setMsg(msg) {{
  document.getElementById('sb-msg').textContent = msg;
}}

// ── Handle sidebar button commands from Python ────────────────
(function() {{
  const cmd = {js_cmd};
  if(!cmd || cmd==='null') return;
  if(cmd.startsWith('addShape:'))      {{ addShape(cmd.split(':')[1]); return; }}
  if(cmd==='deleteSelected')           {{ deleteSelected(); return; }}
  if(cmd==='duplicateSelected')        {{ duplicateSelected(); return; }}
  if(cmd==='clearScene')               {{ clearScene(); return; }}
  if(cmd.startsWith('setMaterial:'))   {{
    const p=cmd.split(':'); setMaterial(p[1], p[2], p[3]); return;
  }}
  if(cmd==='toggleSnapGrid')           {{ toggleSnapGrid(); return; }}
  if(cmd==='toggleWireframe')          {{ toggleWireframe(); return; }}
  if(cmd==='toggleBbox')               {{ toggleBbox(); return; }}
  if(cmd==='toggleDimensions')         {{ toggleDimensions(); return; }}
  if(cmd==='toggleNormals')            {{ toggleNormals(); return; }}
  if(cmd==='toggleOriginAxes')         {{ toggleOriginAxes(); return; }}
  if(cmd==='toggleMeasureMode')        {{ toggleMeasureMode(); return; }}
  if(cmd==='toggleSection')            {{ toggleSection(); return; }}
  if(cmd.startsWith('layerVis:'))      {{ layerVis(cmd.slice(9)); return; }}
  if(cmd.startsWith('layerLock:'))     {{ layerLock(cmd.slice(10)); return; }}
  if(cmd.startsWith('applyPosition:')) {{
    const p=cmd.split(':'); applyPosition(p[1],p[2],p[3]); return;
  }}
}})();

// ── Render loop ───────────────────────────────────────────────
(function animate() {{
  requestAnimationFrame(animate);
  applyOrbit();
  if(selected && gizmoGroup) syncGizmo();
  updateBbox();
  updateCoordHUD();
  renderer.render(scene, cam);
}})();

onResize();
</script>
</body>
</html>"""

st.markdown("## 📐 AI CAD Studio")
components.html(HTML, height=720, scrolling=False)
st.caption(
    "Click shape to select · Drag gizmo arrows to transform · **[X]** AI analyze · **[F]** frame · "
    "**[G]** snap grid · **[W]** wireframe · **[M]** measure · **[D]** duplicate · **[Del]** delete · "
    "Ctrl+Scroll (section mode) moves section plane · Right-drag pans · Scroll zooms"
)