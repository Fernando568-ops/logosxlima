import streamlit as st
import streamlit.components.v1 as components
import json

# ============================================================
#  API CONFIGURATION — reads from st.secrets (OpenRouter)
#  .streamlit/secrets.toml:
#    OPENROUTER_API_KEY = "sk-or-..."
#    OPENROUTER_MODEL   = "anthropic/claude-haiku-4-5"
# ============================================================
try:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
except (KeyError, FileNotFoundError):
    OPENROUTER_API_KEY = ""

try:
    OPENROUTER_MODEL_DEFAULT = st.secrets["OPENROUTER_MODEL"]
except (KeyError, FileNotFoundError):
    OPENROUTER_MODEL_DEFAULT = "anthropic/claude-haiku-4-5"

st.set_page_config(page_title="AI CAD Studio Pro", layout="wide", page_icon="📐")

st.markdown("""
<style>
body, .stApp { background:#060a0f !important; color:#c8d8e8; }
[data-testid="stSidebar"] { background:#080d14 !important; border-right:1px solid #16202c; width:270px !important; }
[data-testid="stSidebar"] * { color:#8a9ab0 !important; font-size:11px !important; }
[data-testid="stSidebar"] h3 { color:#3a6a9a !important; font-size:9px !important;
  text-transform:uppercase; letter-spacing:0.12em; margin:6px 0 2px !important; }
[data-testid="stSidebar"] .stMarkdown hr { border-color:#16202c !important; margin:5px 0 !important; }
.stButton > button {
  background:#0c1520; color:#7a8fa8; border:1px solid #162030;
  border-radius:3px; font-size:10px; width:100%; margin:1px 0;
  padding:4px 6px; font-family:'Courier New',monospace; transition:all 0.1s;
  text-align:left;
}
.stButton > button:hover { background:#162840; border-color:#2a5a8a; color:#a0c0e0; }
.stSelectbox > div > div { background:#080d14 !important; border-color:#16202c !important; font-size:11px !important; font-family:monospace !important; }
.stRadio > div { flex-direction:row !important; gap:6px !important; }
.stRadio label { font-size:10px !important; }
.stTextArea textarea { background:#080d14 !important; color:#a0c8e8 !important; border-color:#16202c !important; font-family:'Courier New',monospace !important; font-size:11px !important; }
.stNumberInput input { background:#080d14 !important; color:#a0c8e8 !important; border-color:#16202c !important; font-family:monospace !important; font-size:11px !important; }
div[data-testid="stSlider"] { padding:0 !important; }
footer, header, #MainMenu { visibility:hidden; }
.block-container { padding-top:0.3rem; padding-bottom:0rem; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📐 CAD Pro")

    if OPENROUTER_API_KEY:
        st.markdown(f"""<div style='background:#0a2010;border:1px solid #1a4a28;border-radius:3px;
        padding:4px 8px;font-size:10px;color:#2aaa60;font-family:monospace;'>
        ✓ OpenRouter connected</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style='background:#200a0a;border:1px solid #4a1a1a;border-radius:3px;
        padding:4px 8px;font-size:10px;color:#cc4444;font-family:monospace;'>
        ✗ No API key in secrets.toml</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── AI Prompt Generator ──────────────────────────────────
    st.markdown("### 🤖 AI Design Generator")
    ai_prompt = st.text_area("Describe your design", placeholder="e.g. A suspension bridge with two towers and cables, or a gear assembly, or a simple chair...", height=80, label_visibility="collapsed")

    MODEL_OPTIONS = {
        "claude-haiku-4-5 (fast)":      "anthropic/claude-haiku-4-5",
        "claude-3-haiku (cheap)":        "anthropic/claude-3-haiku",
        "claude-3.5-haiku (balanced)":   "anthropic/claude-3.5-haiku",
        "claude-3.5-sonnet (powerful)":  "anthropic/claude-3.5-sonnet",
        "gpt-4o-mini (OpenAI cheap)":    "openai/gpt-4o-mini",
        "gemini-flash-1.5 (free tier)":  "google/gemini-flash-1.5",
        "mistral-7b (very cheap)":       "mistralai/mistral-7b-instruct",
    }
    default_label = next((l for l,v in MODEL_OPTIONS.items() if v == OPENROUTER_MODEL_DEFAULT), list(MODEL_OPTIONS.keys())[0])
    selected_model_label = st.selectbox("Model", list(MODEL_OPTIONS.keys()),
        index=list(MODEL_OPTIONS.keys()).index(default_label), label_visibility="collapsed")
    OPENROUTER_MODEL = MODEL_OPTIONS[selected_model_label]

    generate_design = st.button("✦ Generate Design from Prompt", use_container_width=True)
    st.markdown("---")

    # ── Primitives ────────────────────────────────────────────
    st.markdown("### ➕ Primitives")
    c1, c2, c3 = st.columns(3)
    with c1:
        add_box      = st.button("⬛ Box")
        add_cylinder = st.button("⬤ Cyl")
        add_cone     = st.button("▲ Cone")
    with c2:
        add_sphere   = st.button("● Sphere")
        add_torus    = st.button("⭕ Torus")
        add_wedge    = st.button("◤ Wedge")
    with c3:
        add_plane    = st.button("▭ Plane")
        add_pipe     = st.button("| Pipe")
        add_spring   = st.button("~ Spring")

    st.markdown("---")

    # ── Transform ─────────────────────────────────────────────
    st.markdown("### 🎮 Transform")
    mode = st.radio("", ["Move","Rotate","Scale"], horizontal=True, label_visibility="collapsed")
    world_local = st.radio("Space", ["World","Local"], horizontal=True)

    st.markdown("### 📊 Precise Values")
    st.markdown("<div style='font-size:9px;color:#2a4060;font-family:monospace;'>Position X / Y / Z</div>", unsafe_allow_html=True)
    tp1,tp2,tp3 = st.columns(3)
    with tp1: pos_x = st.number_input("px", value=0.0, step=0.25, format="%.3f", label_visibility="collapsed", key="px")
    with tp2: pos_y = st.number_input("py", value=0.0, step=0.25, format="%.3f", label_visibility="collapsed", key="py")
    with tp3: pos_z = st.number_input("pz", value=0.0, step=0.25, format="%.3f", label_visibility="collapsed", key="pz")
    apply_pos = st.button("↳ Set Position")

    st.markdown("<div style='font-size:9px;color:#2a4060;font-family:monospace;'>Rotation X / Y / Z (°)</div>", unsafe_allow_html=True)
    tr1,tr2,tr3 = st.columns(3)
    with tr1: rot_x = st.number_input("rx", value=0.0, step=15.0, format="%.1f", label_visibility="collapsed", key="rx")
    with tr2: rot_y = st.number_input("ry", value=0.0, step=15.0, format="%.1f", label_visibility="collapsed", key="ry")
    with tr3: rot_z = st.number_input("rz", value=0.0, step=15.0, format="%.1f", label_visibility="collapsed", key="rz")
    apply_rot = st.button("↳ Set Rotation")

    st.markdown("<div style='font-size:9px;color:#2a4060;font-family:monospace;'>Scale X / Y / Z</div>", unsafe_allow_html=True)
    ts1,ts2,ts3 = st.columns(3)
    with ts1: sc_x = st.number_input("sx", value=1.0, step=0.1, format="%.3f", label_visibility="collapsed", key="sx")
    with ts2: sc_y = st.number_input("sy", value=1.0, step=0.1, format="%.3f", label_visibility="collapsed", key="sy")
    with ts3: sc_z = st.number_input("sz", value=1.0, step=0.1, format="%.3f", label_visibility="collapsed", key="sz")
    apply_scale = st.button("↳ Set Scale")
    st.markdown("---")

    # ── CAD Operations ────────────────────────────────────────
    st.markdown("### ⚙️ CAD Operations")
    ca1, ca2 = st.columns(2)
    with ca1:
        op_extrude   = st.button("↑ Extrude")
        op_revolve   = st.button("↻ Revolve")
        op_loft      = st.button("◇ Loft")
        op_boolean_u = st.button("∪ Union")
    with ca2:
        op_shell     = st.button("□ Shell")
        op_mirror    = st.button("⟺ Mirror")
        op_array     = st.button("⊞ Array")
        op_boolean_s = st.button("∖ Subtract")

    # Extrude params
    st.markdown("<div style='font-size:9px;color:#2a4060;font-family:monospace;'>Extrude / Shell depth</div>", unsafe_allow_html=True)
    extrude_depth = st.slider("Depth", 0.1, 10.0, 2.0, 0.1, label_visibility="collapsed")
    shell_thickness = st.slider("Shell thickness", 0.05, 2.0, 0.15, 0.05, label_visibility="collapsed")

    # Array params
    st.markdown("<div style='font-size:9px;color:#2a4060;font-family:monospace;'>Array: count / spacing</div>", unsafe_allow_html=True)
    arr1, arr2 = st.columns(2)
    with arr1: array_count   = st.number_input("Count",   value=3, min_value=2, max_value=20, label_visibility="collapsed", key="ac")
    with arr2: array_spacing = st.number_input("Spacing", value=2.0, step=0.5, format="%.1f", label_visibility="collapsed", key="asp")
    arr3, arr4 = st.columns(2)
    with arr3: array_axis    = st.selectbox("Axis", ["X","Y","Z"], label_visibility="collapsed", key="aax")
    with arr4: array_type    = st.selectbox("Type", ["Linear","Radial"], label_visibility="collapsed", key="aty")
    st.markdown("---")

    # ── View Controls ─────────────────────────────────────────
    st.markdown("### 👁 View")
    cv1, cv2 = st.columns(2)
    with cv1:
        toggle_wire   = st.button("⬡ Wire")
        toggle_bbox   = st.button("⬜ BBox")
        toggle_dims   = st.button("↔ Dims")
        toggle_normals = st.button("↑ Normals")
    with cv2:
        toggle_grid   = st.button("# Snap")
        toggle_axes   = st.button("+ Axes")
        toggle_measure= st.button("📐 Measure")
        toggle_section= st.button("✂ Section")

    view_preset = st.selectbox("View", ["Perspective","Top","Front","Right","Isometric"], label_visibility="collapsed")
    apply_view  = st.button("↳ Set View")
    st.markdown("---")

    # ── Material ──────────────────────────────────────────────
    st.markdown("### 🎨 Material")
    mat_type = st.selectbox("Preset", ["Custom","Steel","Aluminium","Brass","Plastic","Concrete","Wood","Glass"], label_visibility="collapsed")
    mc1, mc2 = st.columns(2)
    with mc1: color_pick = st.color_picker("Color", "#4a9eff", label_visibility="collapsed")
    with mc2: roughness  = st.slider("Rough", 0.0, 1.0, 0.4, label_visibility="collapsed")
    mm1, mm2 = st.columns(2)
    with mm1: metalness  = st.slider("Metal", 0.0, 1.0, 0.2, label_visibility="collapsed")
    with mm2: opacity    = st.slider("Alpha", 0.1, 1.0, 1.0, label_visibility="collapsed")
    apply_mat = st.button("Apply Material")
    st.markdown("---")

    # ── Layers ────────────────────────────────────────────────
    st.markdown("### 🗂 Layers")
    layer_name = st.selectbox("Active", ["Layer 0","Construction","Hidden","Dimensions","Section"], label_visibility="collapsed")
    cl1, cl2 = st.columns(2)
    with cl1: layer_vis  = st.button("👁 Toggle")
    with cl2: layer_lock = st.button("🔒 Lock")
    st.markdown("---")

    # ── Scene ─────────────────────────────────────────────────
    st.markdown("### 🗑 Scene")
    cs1, cs2, cs3 = st.columns(3)
    with cs1: delete_sel    = st.button("🗑 Del")
    with cs2: duplicate_sel = st.button("⧉ Dup")
    with cs3: clear_all     = st.button("✕ Clear")
    st.markdown("---")

    # ── AI Analyze ────────────────────────────────────────────
    st.markdown("### 🔬 AI Analyze")
    analysis_mode = st.selectbox("Mode", [
        "General Design Review","Structural Analysis","Dimensional Check",
        "GD&T Suggestions","Manufacturing Feasibility","FEA Pre-check","Assembly Notes",
    ], label_visibility="collapsed")
    ai_detail = st.radio("Detail", ["Brief","Detailed"], horizontal=True)

    st.markdown("""<div style='background:#0a1420;border:1px solid #16304a;border-radius:3px;
    padding:6px 8px;font-size:10px;color:#2a6090;font-family:monospace;line-height:1.8;'>
    [X] Analyze · [E] Extrude · [M] Measure<br>
    [G] Snap · [W] Wire · [F] Frame<br>
    [D] Duplicate · [Del] Delete · [Esc] Deselect
    </div>""", unsafe_allow_html=True)

# ── JS command router ─────────────────────────────────────────
js_cmd = "null"
if add_box:          js_cmd = "'prim:box'"
elif add_sphere:     js_cmd = "'prim:sphere'"
elif add_cylinder:   js_cmd = "'prim:cylinder'"
elif add_cone:       js_cmd = "'prim:cone'"
elif add_torus:      js_cmd = "'prim:torus'"
elif add_wedge:      js_cmd = "'prim:wedge'"
elif add_plane:      js_cmd = "'prim:plane'"
elif add_pipe:       js_cmd = "'prim:pipe'"
elif add_spring:     js_cmd = "'prim:spring'"
elif delete_sel:     js_cmd = "'scene:delete'"
elif duplicate_sel:  js_cmd = "'scene:duplicate'"
elif clear_all:      js_cmd = "'scene:clear'"
elif apply_mat:      js_cmd = f"'mat:apply:{color_pick}:{roughness:.3f}:{metalness:.3f}:{opacity:.3f}:{mat_type}'"
elif apply_pos:      js_cmd = f"'xform:pos:{pos_x:.4f}:{pos_y:.4f}:{pos_z:.4f}'"
elif apply_rot:      js_cmd = f"'xform:rot:{rot_x:.2f}:{rot_y:.2f}:{rot_z:.2f}'"
elif apply_scale:    js_cmd = f"'xform:scale:{sc_x:.4f}:{sc_y:.4f}:{sc_z:.4f}'"
elif op_extrude:     js_cmd = f"'cad:extrude:{extrude_depth:.3f}'"
elif op_revolve:     js_cmd = "'cad:revolve'"
elif op_loft:        js_cmd = "'cad:loft'"
elif op_shell:       js_cmd = f"'cad:shell:{shell_thickness:.3f}'"
elif op_mirror:      js_cmd = "'cad:mirror'"
elif op_array:       js_cmd = f"'cad:array:{array_count}:{array_spacing:.2f}:{array_axis}:{array_type}'"
elif op_boolean_u:   js_cmd = "'cad:boolean:union'"
elif op_boolean_s:   js_cmd = "'cad:boolean:subtract'"
elif toggle_wire:    js_cmd = "'view:wire'"
elif toggle_bbox:    js_cmd = "'view:bbox'"
elif toggle_dims:    js_cmd = "'view:dims'"
elif toggle_normals: js_cmd = "'view:normals'"
elif toggle_grid:    js_cmd = "'view:snap'"
elif toggle_axes:    js_cmd = "'view:axes'"
elif toggle_measure: js_cmd = "'view:measure'"
elif toggle_section: js_cmd = "'view:section'"
elif layer_vis:      js_cmd = f"'layer:vis:{layer_name}'"
elif layer_lock:     js_cmd = f"'layer:lock:{layer_name}'"
elif apply_view:     js_cmd = f"'view:preset:{view_preset}'"

mode_js   = {"Move":"move","Rotate":"rotate","Scale":"scale"}[mode]
space_js  = "world" if world_local == "World" else "local"
detail_js = "detailed" if ai_detail == "Detailed" else "brief"

# ── AI Design Generator prompt (passed as JSON to avoid f-string issues) ──
gen_payload = ""
if generate_design and ai_prompt.strip():
    gen_payload = json.dumps({
        "prompt": ai_prompt.strip(),
        "model": OPENROUTER_MODEL,
        "apiKey": OPENROUTER_API_KEY,
    })

# ── Main HTML Application ──────────────────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
*{{ margin:0;padding:0;box-sizing:border-box; }}
body{{ background:#060a0f;overflow:hidden;font-family:'Courier New',monospace;user-select:none; }}
canvas{{ display:block; }}

/* ── HUD ── */
#hud{{
  position:absolute;top:8px;left:8px;
  background:#060a0fee;border:1px solid #16202c;border-radius:3px;
  padding:6px 10px;font-size:10px;color:#2a4a6a;line-height:1.8;
  pointer-events:none;min-width:230px;
}}
#hud .v{{ color:#3a7aaa; }}
#hud .h{{ color:#1a3a5a; }}
#hud .s{{ color:#4a9aff;font-weight:bold;border-top:1px solid #16202c;margin-top:4px;padding-top:4px; }}

/* ── Status bar ── */
#statusbar{{
  position:absolute;bottom:0;left:0;right:0;height:24px;
  background:#040810ee;border-top:1px solid #12202c;
  display:flex;align-items:center;font-size:10px;color:#2a4060;
}}
.sc{{ padding:0 10px;height:100%;display:flex;align-items:center;border-right:1px solid #0e1820; }}
.sc.on{{ color:#3a8ad0; }}
.sc.warn{{ color:#c09030; }}
#sb-msg{{ flex:1;padding:0 10px; }}
#sb-dist{{ min-width:130px;padding:0 10px;text-align:right; }}

/* ── Properties panel ── */
#props{{
  position:absolute;top:8px;right:8px;width:200px;
  background:#060a0fee;border:1px solid #16202c;border-radius:3px;
  display:none;font-size:10px;
}}
#props-hdr{{
  padding:5px 8px;border-bottom:1px solid #101820;
  color:#2a5a8a;font-size:9px;text-transform:uppercase;letter-spacing:.08em;
  display:flex;justify-content:space-between;
}}
#props-body{{ padding:8px; }}
.pr{{ display:flex;justify-content:space-between;margin:2px 0; }}
.pl{{ color:#1a3a5a; }}
.pv{{ color:#3a7ab8;font-family:monospace; }}
.ph{{ color:#0e2030;text-transform:uppercase;font-size:8px;letter-spacing:.06em;
  margin:5px 0 2px;border-bottom:1px solid #101820;padding-bottom:1px; }}

/* ── Measure panel ── */
#measure-panel{{
  position:absolute;top:8px;left:50%;transform:translateX(-50%);
  background:#04101aee;border:1px solid #164060;border-radius:3px;
  padding:5px 14px;font-size:11px;color:#30b0e0;display:none;
  pointer-events:none;text-align:center;white-space:nowrap;
}}

/* ── AI panels ── */
#ai-gen-panel, #ai-analyze-panel{{
  position:absolute;bottom:32px;right:8px;width:380px;
  background:#040810f4;border:1px solid #16202c;border-radius:3px;
  display:none;flex-direction:column;max-height:55vh;
  box-shadow:0 4px 28px #00000099;
}}
.ai-hdr{{
  display:flex;align-items:center;justify-content:space-between;
  padding:6px 10px;border-bottom:1px solid #101820;
}}
.ai-hdr span{{ color:#2a6aaa;font-size:9px;letter-spacing:.1em;text-transform:uppercase; }}
.ai-close{{ background:none;border:none;color:#2a4060;cursor:pointer;font-size:13px;padding:0 3px; }}
.ai-close:hover{{ color:#e0e8f0; }}
.ai-body{{
  padding:10px;overflow-y:auto;flex:1;
  font-size:11px;color:#7090b0;line-height:1.8;
}}
.ai-tag{{
  background:#0a1e30;border:1px solid #163050;border-radius:2px;
  padding:2px 7px;font-size:9px;color:#2a6090;margin-bottom:7px;display:inline-block;
  text-transform:uppercase;letter-spacing:.06em;
}}
.ai-sec{{ color:#1e5a82;font-size:9px;text-transform:uppercase;letter-spacing:.07em;
  margin:7px 0 2px;border-bottom:1px solid #101820;padding-bottom:1px; }}
.ldg{{ display:flex;align-items:center;gap:6px;color:#1e3a5a; }}
.dot{{ animation:blink 1.4s infinite; }}
.dot:nth-child(2){{ animation-delay:.2s; }}
.dot:nth-child(3){{ animation-delay:.4s; }}
@keyframes blink{{ 0%,80%,100%{{opacity:0;}} 40%{{opacity:1;}} }}

/* ── Operation mode overlay ── */
#op-overlay{{
  position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  background:#040810cc;border:1px solid #1a4060;border-radius:4px;
  padding:10px 20px;font-size:12px;color:#3090d0;
  pointer-events:none;display:none;text-align:center;
}}

/* ── Snap dot ── */
#snap-dot{{
  position:absolute;width:7px;height:7px;background:#30d030;
  border-radius:50%;pointer-events:none;display:none;
  transform:translate(-3px,-3px);
}}
</style>
</head>
<body>

<div id="hud">
  <div><span class="h">CURSOR </span><span class="v" id="hud-cur">--</span></div>
  <div><span class="h">CAM    </span><span class="v" id="hud-cam">--</span></div>
  <div><span class="h">OBJS   </span><span class="v" id="hud-cnt">0</span></div>
  <div id="hud-sel" style="display:none">
    <div class="s" id="hud-name">--</div>
    <div><span class="h">POS  </span><span class="v" id="hud-pos">--</span></div>
    <div><span class="h">ROT  </span><span class="v" id="hud-rot">--</span></div>
    <div><span class="h">SIZE </span><span class="v" id="hud-sz">--</span></div>
    <div><span class="h">HIST </span><span class="v" id="hud-hist">--</span></div>
  </div>
</div>

<div id="statusbar">
  <div class="sc" id="sb-mode">NAVIGATE</div>
  <div class="sc" id="sb-snap">SNAP:OFF</div>
  <div class="sc" id="sb-wire">WIRE:OFF</div>
  <div class="sc" id="sb-xmode">MOVE · WORLD</div>
  <div class="sc" id="sb-msg">Ready — add shapes or use AI Generator</div>
  <div class="sc" id="sb-dist"></div>
</div>

<div id="props">
  <div id="props-hdr"><span>Properties</span><span id="props-type" style="color:#1a4060"></span></div>
  <div id="props-body"></div>
</div>

<div id="measure-panel"><span id="mp-txt">Click first point</span></div>
<div id="op-overlay" id="op-ov"></div>
<div id="snap-dot"></div>

<!-- AI Generate Panel -->
<div id="ai-gen-panel">
  <div class="ai-hdr">
    <span>✦ AI Design Generator</span>
    <button class="ai-close" onclick="closeGen()">✕</button>
  </div>
  <div class="ai-body" id="ai-gen-body">
    <div class="ldg"><span>Generating</span><span class="dot">■</span><span class="dot">■</span><span class="dot">■</span></div>
  </div>
</div>

<!-- AI Analyze Panel -->
<div id="ai-analyze-panel">
  <div class="ai-hdr">
    <span>📐 Claude Analysis</span>
    <button class="ai-close" onclick="closeAnalyze()">✕</button>
  </div>
  <div class="ai-body" id="ai-analyze-body">
    <div class="ldg"><span>Analyzing</span><span class="dot">■</span><span class="dot">■</span><span class="dot">■</span></div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ── Config injected from Python ───────────────────────────────
const OPENROUTER_API_KEY  = {json.dumps(OPENROUTER_API_KEY)};
const ANALYSIS_MODE       = {json.dumps(analysis_mode)};
const AI_DETAIL           = {json.dumps(detail_js)};
let   transformMode       = {json.dumps(mode_js)};
let   transformSpace      = {json.dumps(space_js)};
const GEN_PAYLOAD         = {json.dumps(gen_payload)};

// ── Renderer ──────────────────────────────────────────────────
const renderer = new THREE.WebGLRenderer({{antialias:true, logarithmicDepthBuffer:true}});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.localClippingEnabled = true;
document.body.appendChild(renderer.domElement);
function onResize(){{
  renderer.setSize(innerWidth,innerHeight);
  cam.aspect=innerWidth/innerHeight;
  cam.updateProjectionMatrix();
}}
window.addEventListener('resize',onResize);

// ── Scene ─────────────────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x060a0f);
scene.fog = new THREE.FogExp2(0x060a0f, 0.008);

// ── Camera ────────────────────────────────────────────────────
const cam = new THREE.PerspectiveCamera(48, innerWidth/innerHeight, 0.05, 2000);
const orb = {{theta:0.65, phi:1.05, r:20, tx:0, ty:1, tz:0}};
function applyOrbit(){{
  const sp=Math.sin(orb.phi), cp=Math.cos(orb.phi);
  const st=Math.sin(orb.theta), ct=Math.cos(orb.theta);
  cam.position.set(orb.tx+orb.r*sp*st, orb.ty+orb.r*cp, orb.tz+orb.r*sp*ct);
  cam.lookAt(orb.tx, orb.ty, orb.tz);
}}

// ── Lights ────────────────────────────────────────────────────
scene.add(new THREE.AmbientLight(0x111a28, 1.0));
const key = new THREE.DirectionalLight(0xffffff,1.3);
key.position.set(12,22,10); key.castShadow=true;
key.shadow.mapSize.set(4096,4096);
['left','right','top','bottom'].forEach((s,i)=>key.shadow.camera[s]=[-40,40,40,-40][i]);
key.shadow.bias=-0.0002; scene.add(key);
const fill = new THREE.DirectionalLight(0x1a3060,0.5); fill.position.set(-10,5,-8); scene.add(fill);
const rim  = new THREE.DirectionalLight(0x102040,0.3); rim.position.set(0,-4,-14); scene.add(rim);

// ── Ground ────────────────────────────────────────────────────
const gndMesh = new THREE.Mesh(
  new THREE.PlaneGeometry(400,400),
  new THREE.MeshStandardMaterial({{color:0x070b10,roughness:0.95,metalness:0.05}})
);
gndMesh.rotation.x=-Math.PI/2; gndMesh.receiveShadow=true; gndMesh.name='_ground';
scene.add(gndMesh);

// ── Grids ─────────────────────────────────────────────────────
const gridMaj = new THREE.GridHelper(60,12,0x1a2a3a,0x0e1820);
const gridMin = new THREE.GridHelper(60,60,0x0c1620,0x0a1218);
gridMaj.position.y=0.001; gridMin.position.y=0.002;
scene.add(gridMaj); scene.add(gridMin);

// ── World axes ────────────────────────────────────────────────
let originAxes=null;
function rebuildAxes(){{
  if(originAxes){{ scene.remove(originAxes); originAxes=null; }}
  if(!cadSt.showAxes) return;
  originAxes=new THREE.Group();
  [[1,0,0,0xff2222,'X'],[0,1,0,0x22ff22,'Y'],[0,0,1,0x2244ff,'Z']].forEach(([x,y,z,c,n])=>{{
    const pts=[new THREE.Vector3(0,0,0),new THREE.Vector3(x,y,z).multiplyScalar(6)];
    const l=new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),
      new THREE.LineBasicMaterial({{color:c,depthTest:false}}));
    l.renderOrder=10; originAxes.add(l);
    const tip=new THREE.Mesh(new THREE.ConeGeometry(0.07,0.28,8),
      new THREE.MeshBasicMaterial({{color:c,depthTest:false}}));
    tip.position.set(x*6,y*6,z*6);
    if(x)tip.rotation.z=-Math.PI/2;
    if(z)tip.rotation.x=Math.PI/2;
    tip.renderOrder=10; originAxes.add(tip);
  }});
  scene.add(originAxes);
}}

// ── CAD State ─────────────────────────────────────────────────
const cadSt = {{
  snapGrid:false, snapSize:0.25,
  wireframe:false, showBbox:false, showDims:false, showNormals:false, showAxes:false,
  measureMode:false, sectionMode:false, sectionY:2,
  activeLayer:'Layer 0',
  layers:{{
    'Layer 0':     {{vis:true,locked:false}},
    'Construction':{{vis:true,locked:false}},
    'Hidden':      {{vis:false,locked:false}},
    'Dimensions':  {{vis:true,locked:false}},
    'Section':     {{vis:true,locked:false}},
  }},
  measurePts:[], measureLine:null,
  clippingPlane: new THREE.Plane(new THREE.Vector3(0,-1,0), 2),
  operationMode: null, // 'loft-select', 'boolean-select'
  loftTargets: [],
  booleanTarget: null,
}};

// ── Object registry ───────────────────────────────────────────
let objects=[], selected=null;
const nameCnt={{}};
const objMeta = new Map(); // mesh -> {{bbox, dimGrp, normHelper, layer, history}}
let colorIdx=0;
const COLORS=[0x4a9eff,0xff5555,0x44dd88,0xffcc22,0xaa77ff,0xff8833,0x22ddcc,0xff44aa,0x88ddff,0xff9944];

// ── Operation history per object ──────────────────────────────
function pushHistory(mesh, op){{
  const m=objMeta.get(mesh);
  if(!m) return;
  if(!m.history) m.history=[];
  m.history.push(op);
  updateHUD();
}}

// ── Material presets ──────────────────────────────────────────
const MAT_PRESETS={{
  'Steel':     {{color:'#8a9aaa',rough:0.3,metal:0.9}},
  'Aluminium': {{color:'#b0c0cc',rough:0.25,metal:0.85}},
  'Brass':     {{color:'#c8a840',rough:0.2,metal:0.8}},
  'Plastic':   {{color:'#3a6aaa',rough:0.7,metal:0.0}},
  'Concrete':  {{color:'#707880',rough:0.95,metal:0.0}},
  'Wood':      {{color:'#8a5a30',rough:0.85,metal:0.0}},
  'Glass':     {{color:'#88ccee',rough:0.05,metal:0.1}},
}};

function makeMat(color, rough=0.4, metal=0.2, alpha=1.0){{
  return new THREE.MeshStandardMaterial({{
    color, roughness:rough, metalness:metal,
    transparent:alpha<1.0, opacity:alpha,
    side: THREE.DoubleSide,
  }});
}}

// ── Geometry factories ────────────────────────────────────────
const GEOS={{
  box:      ()=>new THREE.BoxGeometry(1.5,1.5,1.5),
  sphere:   ()=>new THREE.SphereGeometry(0.9,48,48),
  cylinder: ()=>new THREE.CylinderGeometry(0.7,0.7,2.0,48),
  cone:     ()=>new THREE.ConeGeometry(0.8,2.0,48),
  torus:    ()=>new THREE.TorusGeometry(0.8,0.25,20,80),
  wedge:    ()=>{{
    const g=new THREE.BufferGeometry();
    const v=new Float32Array([-0.75,0,-0.75, 0.75,0,-0.75, 0.75,0,0.75, -0.75,0,0.75, -0.75,1.5,-0.75, 0.75,1.5,-0.75]);
    const i=new Uint16Array([0,2,1,0,3,2, 4,1,5,4,0,1, 0,4,3, 1,2,5, 3,5,2,3,4,5]);
    g.setAttribute('position',new THREE.BufferAttribute(v,3));
    g.setIndex(new THREE.BufferAttribute(i,1));
    g.computeVertexNormals(); return g;
  }},
  plane: ()=>new THREE.PlaneGeometry(2.5,2.5,4,4),
  pipe:  ()=>new THREE.TorusGeometry(0.7,0.1,12,64),
  spring:()=>buildSpringGeo(0.6,2.0,12,60),
}};

function buildSpringGeo(radius, height, coils, segs){{
  const pts=[];
  for(let i=0;i<=segs;i++){{
    const t=i/segs;
    const angle=t*coils*Math.PI*2;
    pts.push(new THREE.Vector3(Math.cos(angle)*radius, (t-0.5)*height, Math.sin(angle)*radius));
  }}
  const curve=new THREE.CatmullRomCurve3(pts);
  return new THREE.TubeGeometry(curve, segs*2, 0.06, 8, false);
}}

// ── Add primitive ─────────────────────────────────────────────
function addPrim(type){{
  if(cadSt.layers[cadSt.activeLayer]?.locked){{ setMsg('Layer locked'); return; }}
  nameCnt[type]=(nameCnt[type]||0)+1;
  const col=COLORS[colorIdx++%COLORS.length];
  const mat=makeMat(col);
  const geo=GEOS[type]?GEOS[type]():GEOS.box();
  const mesh=new THREE.Mesh(geo,mat);
  mesh.castShadow=true; mesh.receiveShadow=true;
  const a=Math.random()*Math.PI*2, r=Math.random()*2;
  mesh.position.set(Math.cos(a)*r, 0.8, Math.sin(a)*r);
  mesh.userData={{type, name:type+'_'+nameCnt[type], layer:cadSt.activeLayer}};
  scene.add(mesh); objects.push(mesh);
  objMeta.set(mesh,{{bbox:null,dimGrp:null,normHelper:null,history:['created']}});
  if(cadSt.showBbox) attachBbox(mesh);
  if(!cadSt.layers[cadSt.activeLayer].vis) mesh.visible=false;
  selectObj(mesh);
  setMsg('Added '+mesh.userData.name+' → [E] to extrude, [X] to analyze');
  updObjCount();
}}

// ── Bbox ──────────────────────────────────────────────────────
function attachBbox(mesh){{
  const h=new THREE.BoxHelper(mesh,0x304860);
  h.name='_bbox'; scene.add(h);
  const m=objMeta.get(mesh);
  if(m) m.bbox=h;
  return h;
}}
function detachBbox(mesh){{
  const m=objMeta.get(mesh);
  if(m?.bbox){{ scene.remove(m.bbox); m.bbox=null; }}
}}
function updateAllBboxes(){{
  objMeta.forEach((m,mesh)=>{{ if(m.bbox) m.bbox.update(); }});
}}

// ── Dimension lines ───────────────────────────────────────────
function buildDimGrp(mesh){{
  const g=new THREE.Group(); g.name='_dim';
  const bb=new THREE.Box3().setFromObject(mesh);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  const ctr=new THREE.Vector3(); bb.getCenter(ctr);
  const lm=new THREE.LineBasicMaterial({{color:0x30a0b0,depthTest:false}});
  function ln(a,b){{
    const geo=new THREE.BufferGeometry().setFromPoints([a.clone(),b.clone()]);
    const l=new THREE.Line(geo,lm); l.renderOrder=5; g.add(l);
  }}
  const off=0.35;
  // X
  const xA=new THREE.Vector3(bb.min.x,bb.min.y-off,ctr.z);
  const xB=new THREE.Vector3(bb.max.x,bb.min.y-off,ctr.z);
  ln(xA,xB);
  ln(new THREE.Vector3(bb.min.x,bb.min.y,ctr.z),xA);
  ln(new THREE.Vector3(bb.max.x,bb.min.y,ctr.z),xB);
  // Y
  const yA=new THREE.Vector3(bb.max.x+off,bb.min.y,ctr.z);
  const yB=new THREE.Vector3(bb.max.x+off,bb.max.y,ctr.z);
  ln(yA,yB);
  ln(new THREE.Vector3(bb.max.x,bb.min.y,ctr.z),yA);
  ln(new THREE.Vector3(bb.max.x,bb.max.y,ctr.z),yB);
  // Z
  const zA=new THREE.Vector3(ctr.x,bb.min.y-off,bb.min.z);
  const zB=new THREE.Vector3(ctr.x,bb.min.y-off,bb.max.z);
  ln(zA,zB);
  ln(new THREE.Vector3(ctr.x,bb.min.y,bb.min.z),zA);
  ln(new THREE.Vector3(ctr.x,bb.min.y,bb.max.z),zB);
  scene.add(g);
  return g;
}}
function attachDims(mesh){{
  const m=objMeta.get(mesh); if(!m) return;
  if(m.dimGrp){{ scene.remove(m.dimGrp); }}
  m.dimGrp=buildDimGrp(mesh);
}}
function detachDims(mesh){{
  const m=objMeta.get(mesh); if(!m) return;
  if(m.dimGrp){{ scene.remove(m.dimGrp); m.dimGrp=null; }}
}}

// ── Normal helper ──────────────────────────────────────────────
function attachNormals(mesh){{
  const m=objMeta.get(mesh); if(!m) return;
  try{{
    if(m.normHelper) scene.remove(m.normHelper);
    m.normHelper=new THREE.VertexNormalsHelper(mesh,0.22,0x00ee88);
    scene.add(m.normHelper);
  }}catch(e){{}}
}}
function detachNormals(mesh){{
  const m=objMeta.get(mesh); if(!m) return;
  if(m.normHelper){{ scene.remove(m.normHelper); m.normHelper=null; }}
}}

// ═══════════════════════════════════════════════════════════════
// ── CAD OPERATIONS ─────────────────────────────────────────────
// ═══════════════════════════════════════════════════════════════

// ── Extrude: Scales Y of the object's geometry along the Y axis
// by rebuilding it as a BoxGeometry of matching footprint + depth
function cadExtrude(depth){{
  if(!selected) return setMsg('Select an object to extrude');
  const bb=new THREE.Box3().setFromObject(selected);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  // Replace geometry with extruded box
  selected.geometry.dispose();
  selected.geometry=new THREE.BoxGeometry(sz.x, depth, sz.z);
  selected.position.y = bb.min.y + depth/2;
  cleanup(selected);
  pushHistory(selected, 'extrude:'+depth.toFixed(2));
  updatePropsPanel(selected);
  setMsg('Extruded '+selected.userData.name+' → height '+depth.toFixed(2));
}}

// ── Revolve: spins selected footprint shape around the Y axis
function cadRevolve(){{
  if(!selected) return setMsg('Select an object to revolve');
  const bb=new THREE.Box3().setFromObject(selected);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  const radius=Math.max(sz.x,sz.z)*0.6;
  const height=sz.y;
  selected.geometry.dispose();
  selected.geometry=new THREE.CylinderGeometry(radius,radius,height,64);
  cleanup(selected);
  pushHistory(selected,'revolve');
  setMsg('Revolved '+selected.userData.name+' around Y axis');
}}

// ── Shell: creates a hollow shell by layering a slightly smaller
//   inverted copy inside and combining into a group
function cadShell(thickness){{
  if(!selected) return setMsg('Select an object to shell');
  const bb=new THREE.Box3().setFromObject(selected);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  const inner=new THREE.Mesh(
    new THREE.BoxGeometry(
      Math.max(0.01,sz.x-thickness*2),
      Math.max(0.01,sz.y-thickness*2),
      Math.max(0.01,sz.z-thickness*2)
    ),
    selected.material.clone()
  );
  inner.material.side=THREE.BackSide;
  inner.position.copy(selected.position);
  inner.rotation.copy(selected.rotation);
  inner.name=selected.userData.name+'_shell_inner';
  inner.userData={{type:'shell_inner',layer:selected.userData.layer,name:inner.name}};
  scene.add(inner);
  objects.push(inner);
  objMeta.set(inner,{{bbox:null,dimGrp:null,normHelper:null,history:['shell_inner']}});
  selected.material.transparent=true;
  selected.material.opacity=0.35;
  selected.material.side=THREE.FrontSide;
  selected.material.needsUpdate=true;
  pushHistory(selected,'shell:'+thickness.toFixed(3));
  setMsg('Shelled '+selected.userData.name+' — wall '+thickness.toFixed(3)+' units');
  updObjCount();
}}

// ── Mirror: mirrors selected object across an axis
function cadMirror(axis){{
  if(!selected) return setMsg('Select an object to mirror');
  const orig=selected;
  const mirr=orig.clone();
  mirr.material=orig.material.clone();
  const n=orig.userData.type;
  nameCnt[n]=(nameCnt[n]||0)+1;
  mirr.userData={{...orig.userData, name:n+'_'+nameCnt[n]}};
  mirr.position.copy(orig.position);
  mirr.rotation.copy(orig.rotation);
  mirr.scale.copy(orig.scale);
  if(axis==='X') mirr.scale.x*=-1;
  else if(axis==='Y') mirr.scale.y*=-1;
  else mirr.scale.z*=-1;
  scene.add(mirr); objects.push(mirr);
  objMeta.set(mirr,{{bbox:null,dimGrp:null,normHelper:null,history:['mirrored_from:'+orig.userData.name]}});
  if(cadSt.showBbox) attachBbox(mirr);
  selectObj(mirr);
  pushHistory(mirr,'mirror:'+axis);
  setMsg('Mirrored '+orig.userData.name+' on '+axis+' axis → '+mirr.userData.name);
  updObjCount();
}}

// ── Array: creates N copies along axis or radially
function cadArray(count, spacing, axis, type){{
  if(!selected) return setMsg('Select an object to array');
  const src=selected;
  const created=[];
  for(let i=1;i<count;i++){{
    const cp=src.clone();
    cp.material=src.material.clone();
    const n=src.userData.type;
    nameCnt[n]=(nameCnt[n]||0)+1;
    cp.userData={{...src.userData, name:n+'_'+nameCnt[n]}};
    if(type==='Linear'){{
      cp.position.copy(src.position);
      if(axis==='X') cp.position.x+=spacing*i;
      else if(axis==='Y') cp.position.y+=spacing*i;
      else cp.position.z+=spacing*i;
    }} else {{
      // Radial
      const angle=(Math.PI*2/count)*i;
      cp.position.x=src.position.x+Math.cos(angle)*spacing;
      cp.position.z=src.position.z+Math.sin(angle)*spacing;
      cp.position.y=src.position.y;
      cp.rotation.y=angle;
    }}
    scene.add(cp); objects.push(cp);
    objMeta.set(cp,{{bbox:null,dimGrp:null,normHelper:null,history:['array_copy_'+i]}});
    if(cadSt.showBbox) attachBbox(cp);
    created.push(cp);
  }}
  pushHistory(src,'array:'+type+':'+count);
  setMsg('Array: '+count+' copies of '+src.userData.name+' ('+type+')');
  updObjCount();
}}

// ── Loft: builds a lofted shape between 2 selected meshes
//   by interpolating their bounding boxes into a TubeGeometry
function startLoft(){{
  cadSt.operationMode='loft-select';
  cadSt.loftTargets=[];
  setOpOverlay('LOFT — click 2 objects as profiles (then auto-executes)');
  setMsg('LOFT: click first profile object');
  document.getElementById('sb-mode').textContent='LOFT';
  document.getElementById('sb-mode').className='sc on';
}}

function finishLoft(){{
  const [a,b]=cadSt.loftTargets;
  const bbA=new THREE.Box3().setFromObject(a);
  const bbB=new THREE.Box3().setFromObject(b);
  const cA=new THREE.Vector3(); bbA.getCenter(cA);
  const cB=new THREE.Vector3(); bbB.getCenter(cB);
  const szA=new THREE.Vector3(); bbA.getSize(szA);
  const szB=new THREE.Vector3(); bbB.getSize(szB);

  // Build a TubeGeometry path between centers
  const midY=(cA.y+cB.y)/2+1.5;
  const curve=new THREE.CatmullRomCurve3([
    cA.clone(),
    new THREE.Vector3((cA.x+cB.x)/2,(cA.y+cB.y)/2+Math.abs(cB.y-cA.y)*0.5+0.5,(cA.z+cB.z)/2),
    cB.clone()
  ]);
  const rA=Math.max(szA.x,szA.z)*0.45;
  const rB=Math.max(szB.x,szB.z)*0.45;
  const segs=40;
  // Vary tube radius along path
  const radii=[];
  for(let i=0;i<=segs;i++) radii.push(rA+(rB-rA)*(i/segs));

  const geo=new THREE.TubeGeometry(curve, segs, (rA+rB)/2, 16, false);
  const mat=makeMat(COLORS[colorIdx++%COLORS.length],0.4,0.2);
  const loftMesh=new THREE.Mesh(geo,mat);
  loftMesh.castShadow=true; loftMesh.receiveShadow=true;
  nameCnt['loft']=(nameCnt['loft']||0)+1;
  loftMesh.userData={{type:'loft',name:'loft_'+nameCnt['loft'],layer:cadSt.activeLayer}};
  scene.add(loftMesh); objects.push(loftMesh);
  objMeta.set(loftMesh,{{bbox:null,dimGrp:null,normHelper:null,history:['loft:'+a.userData.name+'+'+b.userData.name]}});

  cadSt.operationMode=null; cadSt.loftTargets=[];
  setOpOverlay(null);
  selectObj(loftMesh);
  setMsg('Lofted '+a.userData.name+' → '+b.userData.name+' = '+loftMesh.userData.name);
  updObjCount();
  document.getElementById('sb-mode').textContent='NAVIGATE';
  document.getElementById('sb-mode').className='sc';
}}

// ── Boolean union: merges two meshes' geometry via BufferGeometry merge
function startBoolean(op){{
  cadSt.operationMode='boolean-'+op;
  cadSt.booleanTarget=selected;
  setOpOverlay('BOOLEAN '+op.toUpperCase()+' — click the second object');
  setMsg('BOOLEAN '+op+': click second object');
  document.getElementById('sb-mode').textContent='BOOL:'+op.toUpperCase();
  document.getElementById('sb-mode').className='sc warn';
}}

function finishBoolean(op, objA, objB){{
  if(op==='union'){{
    // Merge geometries
    const gA=objA.geometry.clone();
    gA.applyMatrix4(objA.matrixWorld);
    const gB=objB.geometry.clone();
    gB.applyMatrix4(objB.matrixWorld);
    const merged=THREE.BufferGeometryUtils ?
      THREE.BufferGeometryUtils.mergeBufferGeometries([gA,gB]) :
      mergeGeoFallback(gA,gB);
    if(merged){{
      const mat=makeMat(objA.material.color.getHex(), objA.material.roughness, objA.material.metalness);
      const result=new THREE.Mesh(merged,mat);
      result.castShadow=true; result.receiveShadow=true;
      nameCnt['union']=(nameCnt['union']||0)+1;
      result.userData={{type:'union',name:'union_'+nameCnt['union'],layer:cadSt.activeLayer}};
      scene.add(result); objects.push(result);
      objMeta.set(result,{{bbox:null,dimGrp:null,normHelper:null,history:['union:'+objA.userData.name+'+'+objB.userData.name]}});
      removeObj(objA); removeObj(objB);
      selectObj(result);
      setMsg('Boolean union: '+result.userData.name);
      updObjCount();
    }}
  }} else if(op==='subtract'){{
    // Approximate subtract: scale A to exclude B's volume (visual approximation)
    const bbB=new THREE.Box3().setFromObject(objB);
    const szB=new THREE.Vector3(); bbB.getSize(szB);
    const bbA=new THREE.Box3().setFromObject(objA);
    const cA=new THREE.Vector3(); bbA.getCenter(cA);
    // Create a "hole" visual with clipping
    objA.material.clippingPlanes=[
      new THREE.Plane(new THREE.Vector3(1,0,0),-bbB.min.x),
      new THREE.Plane(new THREE.Vector3(-1,0,0),bbB.max.x),
    ];
    renderer.localClippingEnabled=true;
    pushHistory(objA,'subtract:'+objB.userData.name);
    removeObj(objB);
    setMsg('Boolean subtract: clipped '+objB.userData.name+' from '+objA.userData.name);
    updObjCount();
  }}
  cadSt.operationMode=null; cadSt.booleanTarget=null;
  setOpOverlay(null);
  document.getElementById('sb-mode').textContent='NAVIGATE';
  document.getElementById('sb-mode').className='sc';
}}

function mergeGeoFallback(gA,gB){{
  // Manual merge of position buffers
  const posA=gA.getAttribute('position');
  const posB=gB.getAttribute('position');
  const merged=new Float32Array(posA.count*3+posB.count*3);
  merged.set(posA.array,0);
  merged.set(posB.array,posA.count*3);
  const out=new THREE.BufferGeometry();
  out.setAttribute('position',new THREE.BufferAttribute(merged,3));
  out.computeVertexNormals();
  return out;
}}

// ── Remove object helper ───────────────────────────────────────
function removeObj(mesh){{
  const m=objMeta.get(mesh);
  if(m?.bbox)     scene.remove(m.bbox);
  if(m?.dimGrp)   scene.remove(m.dimGrp);
  if(m?.normHelper) scene.remove(m.normHelper);
  objMeta.delete(mesh);
  scene.remove(mesh);
  objects=objects.filter(o=>o!==mesh);
  if(selected===mesh){{ selected=null; buildGizmo(); updatePropsPanel(null); }}
}}

function cleanup(mesh){{
  detachBbox(mesh);
  detachDims(mesh);
  detachNormals(mesh);
  if(cadSt.showBbox) attachBbox(mesh);
  if(cadSt.showDims) attachDims(mesh);
  if(cadSt.showNormals) attachNormals(mesh);
  if(gizmoGroup) buildGizmo();
  syncGizmo();
}}

// ══════════════════════════════════════════════════════════════
// ── GIZMO SYSTEM ─────────────────────────────────────────────
// ══════════════════════════════════════════════════════════════
let gizmoGroup=null;
const AX={{x:0xff2222,y:0x22ee22,z:0x2244ff}};

function buildGizmo(){{
  if(gizmoGroup){{ scene.remove(gizmoGroup); gizmoGroup=null; }}
  if(!selected) return;
  gizmoGroup=new THREE.Group(); gizmoGroup.name='_gizmo';
  if(transformMode==='move') buildMoveGiz();
  else if(transformMode==='rotate') buildRotGiz();
  else buildScaleGiz();
  scene.add(gizmoGroup);
  syncGizmo();
}}
function buildMoveGiz(){{
  ['x','y','z'].forEach(ax=>{{
    const shaft=new THREE.Mesh(new THREE.CylinderGeometry(0.035,0.035,1.9,8),
      new THREE.MeshBasicMaterial({{color:AX[ax],depthTest:false}}));
    const tip=new THREE.Mesh(new THREE.ConeGeometry(0.1,0.3,8),
      new THREE.MeshBasicMaterial({{color:AX[ax],depthTest:false}}));
    tip.position.y=1.1;
    const arr=new THREE.Group(); arr.add(shaft,tip); arr.userData.axis=ax;
    if(ax==='x'){{arr.rotation.z=-Math.PI/2;arr.position.x=1.0;}}
    else if(ax==='y') arr.position.y=1.0;
    else{{arr.rotation.x=Math.PI/2;arr.position.z=1.0;}}
    gizmoGroup.add(arr);
  }});
  [['xz',0xeeee00,[-Math.PI/2,0,0],[0.5,0,0.5]],
   ['xy',0x00eeee,[0,0,0],[0.5,0.5,0]],
   ['yz',0xee00ee,[0,Math.PI/2,0],[0,0.5,0.5]]].forEach(([ax,c,rot,pos])=>{{
    const sq=new THREE.Mesh(new THREE.PlaneGeometry(0.42,0.42),
      new THREE.MeshBasicMaterial({{color:c,transparent:true,opacity:0.22,side:THREE.DoubleSide,depthTest:false}}));
    sq.userData.axis=ax;
    sq.rotation.set(...rot); sq.position.set(...pos);
    gizmoGroup.add(sq);
  }});
}}
function buildRotGiz(){{
  [['x',0xff2222,[0,0,Math.PI/2]],['y',0x22ee22,[0,0,0]],['z',0x2244ff,[Math.PI/2,0,0]]].forEach(([ax,c,rot])=>{{
    const ring=new THREE.Mesh(new THREE.TorusGeometry(1.1,0.035,8,64),
      new THREE.MeshBasicMaterial({{color:c,depthTest:false}}));
    ring.userData.axis=ax; ring.rotation.set(...rot);
    gizmoGroup.add(ring);
  }});
}}
function buildScaleGiz(){{
  ['x','y','z'].forEach(ax=>{{
    const shaft=new THREE.Mesh(new THREE.CylinderGeometry(0.035,0.035,1.9,8),
      new THREE.MeshBasicMaterial({{color:AX[ax],depthTest:false}}));
    const cube=new THREE.Mesh(new THREE.BoxGeometry(0.2,0.2,0.2),
      new THREE.MeshBasicMaterial({{color:AX[ax],depthTest:false}}));
    cube.position.y=1.1;
    const arr=new THREE.Group(); arr.add(shaft,cube); arr.userData.axis=ax;
    if(ax==='x'){{arr.rotation.z=-Math.PI/2;arr.position.x=1.0;}}
    else if(ax==='y') arr.position.y=1.0;
    else{{arr.rotation.x=Math.PI/2;arr.position.z=1.0;}}
    gizmoGroup.add(arr);
  }});
  const uni=new THREE.Mesh(new THREE.SphereGeometry(0.13,8,8),
    new THREE.MeshBasicMaterial({{color:0xffffff,depthTest:false}}));
  uni.userData.axis='xyz'; gizmoGroup.add(uni);
}}
function syncGizmo(){{
  if(!selected||!gizmoGroup) return;
  gizmoGroup.position.copy(selected.position);
  const bb=new THREE.Box3().setFromObject(selected);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  const sc=Math.max(sz.x,sz.y,sz.z)*0.40+0.6;
  gizmoGroup.scale.setScalar(sc);
  if(transformSpace==='local') gizmoGroup.rotation.copy(selected.rotation);
  else gizmoGroup.rotation.set(0,0,0);
}}

// ── Select ────────────────────────────────────────────────────
function selectObj(obj){{
  if(selected&&selected!==obj){{
    selected.material.emissive?.setHex(0x000000);
    if(!cadSt.showDims) detachDims(selected);
    if(!cadSt.showNormals) detachNormals(selected);
  }}
  selected=obj;
  if(selected){{
    selected.material.emissive?.setHex(0x0d2840);
    buildGizmo(); syncGizmo();
    if(cadSt.showDims) attachDims(selected);
    if(cadSt.showNormals) attachNormals(selected);
    updatePropsPanel(selected);
    updateHUD();
    setMsg('['+selected.userData.name+'] · E=extrude · X=analyze · D=dup · F=frame');
    document.getElementById('sb-xmode').textContent=transformMode.toUpperCase()+' · '+transformSpace.toUpperCase();
  }} else {{
    if(gizmoGroup){{ scene.remove(gizmoGroup); gizmoGroup=null; }}
    updatePropsPanel(null);
    updateHUD();
  }}
}}

// ── Properties panel ──────────────────────────────────────────
function updatePropsPanel(mesh){{
  const panel=document.getElementById('props');
  if(!mesh){{ panel.style.display='none'; return; }}
  panel.style.display='block';
  document.getElementById('props-type').textContent=mesh.userData.type?.toUpperCase()||'';
  const bb=new THREE.Box3().setFromObject(mesh);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  const p=mesh.position, r=mesh.rotation, s=mesh.scale;
  const col='#'+mesh.material.color.getHexString();
  const m=objMeta.get(mesh);
  const hist=m?.history?.join(' → ')||'--';
  document.getElementById('props-body').innerHTML=`
    <div class="ph">Location</div>
    <div class="pr"><span class="pl">X</span><span class="pv">${{p.x.toFixed(3)}}</span></div>
    <div class="pr"><span class="pl">Y</span><span class="pv">${{p.y.toFixed(3)}}</span></div>
    <div class="pr"><span class="pl">Z</span><span class="pv">${{p.z.toFixed(3)}}</span></div>
    <div class="ph">Rotation °</div>
    <div class="pr"><span class="pl">Rx</span><span class="pv">${{(r.x*180/Math.PI).toFixed(1)}}</span></div>
    <div class="pr"><span class="pl">Ry</span><span class="pv">${{(r.y*180/Math.PI).toFixed(1)}}</span></div>
    <div class="pr"><span class="pl">Rz</span><span class="pv">${{(r.z*180/Math.PI).toFixed(1)}}</span></div>
    <div class="ph">Bounding Box</div>
    <div class="pr"><span class="pl">W</span><span class="pv">${{sz.x.toFixed(3)}}</span></div>
    <div class="pr"><span class="pl">H</span><span class="pv">${{sz.y.toFixed(3)}}</span></div>
    <div class="pr"><span class="pl">D</span><span class="pv">${{sz.z.toFixed(3)}}</span></div>
    <div class="pr"><span class="pl">Vol≈</span><span class="pv">${{(sz.x*sz.y*sz.z).toFixed(3)}} u³</span></div>
    <div class="ph">Material</div>
    <div class="pr"><span class="pl">Color</span><span class="pv">${{col}}</span></div>
    <div class="pr"><span class="pl">Rough</span><span class="pv">${{mesh.material.roughness?.toFixed(3)||'--'}}</span></div>
    <div class="pr"><span class="pl">Metal</span><span class="pv">${{mesh.material.metalness?.toFixed(3)||'--'}}</span></div>
    <div class="ph">CAD History</div>
    <div class="pr" style="flex-direction:column;gap:1px"><span class="pv" style="font-size:9px;color:#1e4060;word-break:break-all;">${{hist}}</span></div>
    <div class="ph">Info</div>
    <div class="pr"><span class="pl">Layer</span><span class="pv">${{mesh.userData.layer||'Layer 0'}}</span></div>
    <div class="pr"><span class="pl">Scale</span><span class="pv">${{s.x.toFixed(2)}}, ${{s.y.toFixed(2)}}, ${{s.z.toFixed(2)}}</span></div>
  `;
}}

// ── HUD ───────────────────────────────────────────────────────
function updateHUD(){{
  const cp=cam.position;
  document.getElementById('hud-cam').textContent=
    cp.x.toFixed(1)+', '+cp.y.toFixed(1)+', '+cp.z.toFixed(1);
  document.getElementById('hud-cnt').textContent=objects.length;
  if(selected){{
    const sp=selected.position, sr=selected.rotation;
    const bb=new THREE.Box3().setFromObject(selected);
    const sz=new THREE.Vector3(); bb.getSize(sz);
    const m=objMeta.get(selected);
    document.getElementById('hud-sel').style.display='block';
    document.getElementById('hud-name').textContent=selected.userData.name;
    document.getElementById('hud-pos').textContent=sp.x.toFixed(2)+', '+sp.y.toFixed(2)+', '+sp.z.toFixed(2);
    document.getElementById('hud-rot').textContent=(sr.x*57.3).toFixed(1)+'°, '+(sr.y*57.3).toFixed(1)+'°, '+(sr.z*57.3).toFixed(1)+'°';
    document.getElementById('hud-sz').textContent=sz.x.toFixed(2)+' × '+sz.y.toFixed(2)+' × '+sz.z.toFixed(2);
    document.getElementById('hud-hist').textContent=(m?.history||[]).slice(-2).join(' → ')||'--';
  }} else {{
    document.getElementById('hud-sel').style.display='none';
  }}
}}
function updObjCount(){{ document.getElementById('hud-cnt').textContent=objects.length; }}

// ── View toggle helpers ───────────────────────────────────────
function toggleWire(){{
  cadSt.wireframe=!cadSt.wireframe;
  objects.forEach(o=>{{ if(o.material) o.material.wireframe=cadSt.wireframe; }});
  document.getElementById('sb-wire').textContent='WIRE:'+(cadSt.wireframe?'ON':'OFF');
  document.getElementById('sb-wire').className='sc'+(cadSt.wireframe?' on':'');
  setMsg('Wireframe '+(cadSt.wireframe?'ON':'OFF'));
}}
function toggleBbox(){{
  cadSt.showBbox=!cadSt.showBbox;
  objects.forEach(o=>{{
    if(cadSt.showBbox) attachBbox(o);
    else detachBbox(o);
  }});
  setMsg('Bounding boxes '+(cadSt.showBbox?'ON':'OFF'));
}}
function toggleDims(){{
  cadSt.showDims=!cadSt.showDims;
  if(!cadSt.showDims) objMeta.forEach((_,m)=>detachDims(m));
  else if(selected) attachDims(selected);
  setMsg('Dimension lines '+(cadSt.showDims?'ON (selected)':'OFF'));
}}
function toggleNormals(){{
  cadSt.showNormals=!cadSt.showNormals;
  if(!cadSt.showNormals) objMeta.forEach((_,m)=>detachNormals(m));
  else if(selected) attachNormals(selected);
  setMsg('Normals '+(cadSt.showNormals?'ON':'OFF'));
}}
function toggleSnap(){{
  cadSt.snapGrid=!cadSt.snapGrid;
  document.getElementById('sb-snap').textContent='SNAP:'+(cadSt.snapGrid?cadSt.snapSize:'OFF');
  document.getElementById('sb-snap').className='sc'+(cadSt.snapGrid?' on':'');
  setMsg('Snap '+(cadSt.snapGrid?'ON ('+cadSt.snapSize+')':'OFF'));
}}
function toggleAxes(){{
  cadSt.showAxes=!cadSt.showAxes;
  rebuildAxes();
  setMsg('Origin axes '+(cadSt.showAxes?'ON':'OFF'));
}}
function toggleMeasure(){{
  cadSt.measureMode=!cadSt.measureMode;
  cadSt.measurePts=[];
  if(cadSt.measureLine){{ scene.remove(cadSt.measureLine); cadSt.measureLine=null; }}
  const mp=document.getElementById('measure-panel');
  mp.style.display=cadSt.measureMode?'block':'none';
  if(cadSt.measureMode){{
    document.getElementById('mp-txt').textContent='Click 1st point';
    document.getElementById('sb-mode').textContent='MEASURE';
    document.getElementById('sb-mode').className='sc on';
  }} else {{
    document.getElementById('sb-mode').textContent='NAVIGATE';
    document.getElementById('sb-mode').className='sc';
  }}
  setMsg('Measure mode '+(cadSt.measureMode?'ON':'OFF'));
}}
function toggleSection(){{
  cadSt.sectionMode=!cadSt.sectionMode;
  if(cadSt.sectionMode){{
    objects.forEach(o=>{{ o.material.clippingPlanes=[cadSt.clippingPlane]; o.material.clipShadows=true; }});
    renderer.localClippingEnabled=true;
    setMsg('Section plane ON at Y='+cadSt.sectionY.toFixed(2)+' — Ctrl+scroll to move');
  }} else {{
    objects.forEach(o=>{{ o.material.clippingPlanes=[]; }});
    renderer.localClippingEnabled=false;
    setMsg('Section plane OFF');
  }}
}}
function setView(preset){{
  if(preset==='Top'){{     orb.phi=0.01; orb.theta=0; }}
  else if(preset==='Front'){{ orb.phi=Math.PI/2; orb.theta=0; }}
  else if(preset==='Right'){{ orb.phi=Math.PI/2; orb.theta=Math.PI/2; }}
  else if(preset==='Isometric'){{ orb.phi=0.9553; orb.theta=0.7854; }}
  else{{ orb.phi=1.05; orb.theta=0.65; }}
  setMsg('View: '+preset);
}}
function layerVis(n){{
  if(!cadSt.layers[n]) return;
  cadSt.layers[n].vis=!cadSt.layers[n].vis;
  objects.forEach(o=>{{ if(o.userData.layer===n) o.visible=cadSt.layers[n].vis; }});
  setMsg('Layer ['+n+'] '+(cadSt.layers[n].vis?'visible':'hidden'));
}}
function layerLock(n){{
  if(!cadSt.layers[n]) return;
  cadSt.layers[n].locked=!cadSt.layers[n].locked;
  setMsg('Layer ['+n+'] '+(cadSt.layers[n].locked?'LOCKED':'unlocked'));
}}

// ── Duplicate / Delete / Frame ─────────────────────────────────
function duplicate(){{
  if(!selected) return setMsg('Nothing selected');
  const src=selected;
  const cp=src.clone();
  cp.material=src.material.clone();
  const t=src.userData.type;
  nameCnt[t]=(nameCnt[t]||0)+1;
  cp.userData={{...src.userData,name:t+'_'+nameCnt[t]}};
  cp.position.x+=1.8;
  scene.add(cp); objects.push(cp);
  objMeta.set(cp,{{bbox:null,dimGrp:null,normHelper:null,history:['dup_of:'+src.userData.name]}});
  if(cadSt.showBbox) attachBbox(cp);
  selectObj(cp); updObjCount();
  setMsg('Duplicated → '+cp.userData.name);
}}
function deleteSel(){{
  if(!selected) return setMsg('Nothing selected');
  removeObj(selected); selected=null;
  if(gizmoGroup){{ scene.remove(gizmoGroup); gizmoGroup=null; }}
  setMsg('Deleted'); updObjCount();
}}
function clearScene(){{
  [...objects].forEach(o=>removeObj(o));
  objects=[]; colorIdx=0;
  Object.keys(nameCnt).forEach(k=>delete nameCnt[k]);
  selected=null;
  closeGen(); closeAnalyze();
  setMsg('Scene cleared'); updObjCount();
}}
function frameSelected(){{
  if(!selected){{ orb.r=22;orb.tx=0;orb.ty=1;orb.tz=0;setMsg('Framed scene');return; }}
  const bb=new THREE.Box3().setFromObject(selected);
  const ctr=new THREE.Vector3(); bb.getCenter(ctr);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  orb.tx=ctr.x; orb.ty=ctr.y; orb.tz=ctr.z;
  orb.r=Math.max(sz.x,sz.y,sz.z)*2.8+4;
  setMsg('Framed: '+selected.userData.name);
}}

// ── Apply xform from sidebar ───────────────────────────────────
function applyPos(x,y,z){{
  if(!selected) return setMsg('No object selected');
  selected.position.set(parseFloat(x),parseFloat(y),parseFloat(z));
  syncGizmo(); updateAllBboxes(); updatePropsPanel(selected);
  pushHistory(selected,'set_pos');
  setMsg('Position set to '+x+', '+y+', '+z);
}}
function applyRot(rx,ry,rz){{
  if(!selected) return setMsg('No object selected');
  selected.rotation.set(rx*Math.PI/180, ry*Math.PI/180, rz*Math.PI/180);
  syncGizmo(); updateAllBboxes(); updatePropsPanel(selected);
  pushHistory(selected,'set_rot');
  setMsg('Rotation set to '+rx+'°, '+ry+'°, '+rz+'°');
}}
function applyScale(sx,sy,sz){{
  if(!selected) return setMsg('No object selected');
  selected.scale.set(parseFloat(sx),parseFloat(sy),parseFloat(sz));
  syncGizmo(); updateAllBboxes(); updatePropsPanel(selected);
  pushHistory(selected,'set_scale');
  setMsg('Scale set to '+sx+', '+sy+', '+sz);
}}
function applyMat(hexStr,rough,metal,alpha,preset){{
  if(!selected) return setMsg('Select an object first');
  if(preset&&preset!=='Custom'&&MAT_PRESETS[preset]){{
    const p=MAT_PRESETS[preset];
    selected.material.color.set(p.color);
    selected.material.roughness=p.rough;
    selected.material.metalness=p.metal;
  }} else {{
    selected.material.color.set(hexStr);
    selected.material.roughness=parseFloat(rough);
    selected.material.metalness=parseFloat(metal);
  }}
  selected.material.transparent=parseFloat(alpha)<1.0;
  selected.material.opacity=parseFloat(alpha);
  selected.material.needsUpdate=true;
  pushHistory(selected,'mat:'+(preset!=='Custom'?preset:hexStr));
  updatePropsPanel(selected);
  setMsg('Material applied to '+selected.userData.name);
}}
function setOpOverlay(msg){{
  const el=document.getElementById('op-overlay');
  if(!msg){{ el.style.display='none'; return; }}
  el.textContent=msg; el.style.display='block';
}}

// ══════════════════════════════════════════════════════════════
// ── AI DESIGN GENERATOR ──────────────────────────────────────
// ══════════════════════════════════════════════════════════════

function closeGen(){{ document.getElementById('ai-gen-panel').style.display='none'; }}
function closeAnalyze(){{ document.getElementById('ai-analyze-panel').style.display='none'; }}

async function runAIGenerator(payload){{
  const panel=document.getElementById('ai-gen-panel');
  const body=document.getElementById('ai-gen-body');
  panel.style.display='flex';
  body.innerHTML='<div class="ldg"><span>Generating design</span><span class="dot">■</span><span class="dot">■</span><span class="dot">■</span></div>';
  setMsg('Asking Claude to generate design…');

  const systemPrompt=`You are an expert CAD automation engine. The user will describe a 3D design.
You must respond with ONLY a valid JSON object — no markdown, no explanation, no preamble.
The JSON must have this exact schema:
{{
  "name": "string — short name of the design",
  "description": "string — 1 sentence summary",
  "objects": [
    {{
      "id": "unique string id",
      "name": "string",
      "type": "box|sphere|cylinder|cone|torus|wedge|plane|pipe|spring",
      "position": [x, y, z],
      "rotation": [rx_deg, ry_deg, rz_deg],
      "scale": [sx, sy, sz],
      "color": "#rrggbb hex string",
      "roughness": 0.0-1.0,
      "metalness": 0.0-1.0,
      "operations": ["optional list of CAD ops already applied conceptually, e.g. extruded, revolved"],
      "note": "brief engineering note about this part"
    }}
  ],
  "notes": "overall design notes"
}}
Rules:
- Use realistic engineering proportions scaled in meters (1 unit = 1m).
- Place objects so they form a coherent assembly. Ground level is Y=0.
- Y is UP. Use position[1] to stack parts vertically.
- For bridges: use boxes for deck, cylinders for piers, planes or boxes for cables.
- For gears: use cylinders with torus rings on top.
- For buildings: stack box floors, use cylinders for pillars.
- Create enough parts to make the design recognizable (6–20 objects typical).
- Make colors engineering-realistic (steel=grey, concrete=light grey, wood=brown, glass=light blue).
- Never return anything except the JSON object.`;

  try{{
    const resp=await fetch('https://openrouter.ai/api/v1/chat/completions',{{
      method:'POST',
      headers:{{
        'Authorization':'Bearer '+payload.apiKey,
        'Content-Type':'application/json',
        'HTTP-Referer':'https://ai-cad-studio.streamlit.app',
        'X-Title':'AI CAD Studio Pro',
      }},
      body:JSON.stringify({{
        model:payload.model,
        max_tokens:2500,
        temperature:0.4,
        messages:[
          {{role:'system',content:systemPrompt}},
          {{role:'user',content:'Design: '+payload.prompt}},
        ],
      }}),
    }});
    const data=await resp.json();
    if(!resp.ok){{
      const e=data.error?.message||resp.statusText;
      body.innerHTML='<div style="color:#cc4444;font-size:11px;">✗ API Error '+resp.status+': '+e+'</div>';
      return setMsg('Generator API error '+resp.status);
    }}
    const rawText=data.choices?.[0]?.message?.content||'';
    let design;
    try{{
      const clean=rawText.replace(/```json|```/g,'').trim();
      design=JSON.parse(clean);
    }} catch(pe){{
      body.innerHTML='<div style="color:#cc4444;font-size:11px;">✗ Could not parse design JSON.<br><pre style="font-size:9px;color:#444;white-space:pre-wrap;">'+rawText.slice(0,400)+'</pre></div>';
      return setMsg('Parse error — model may not support JSON output');
    }}

    // Clear scene and build design
    clearScene();
    const built=[];
    for(const obj of (design.objects||[])){{
      const type=obj.type||'box';
      const geo=GEOS[type]?GEOS[type]():GEOS.box();
      const mat=makeMat(
        obj.color||'#888888',
        obj.roughness??0.4,
        obj.metalness??0.2
      );
      const mesh=new THREE.Mesh(geo,mat);
      mesh.castShadow=true; mesh.receiveShadow=true;
      const p=obj.position||[0,0,0];
      const r=obj.rotation||[0,0,0];
      const s=obj.scale||[1,1,1];
      mesh.position.set(p[0],p[1],p[2]);
      mesh.rotation.set(r[0]*Math.PI/180, r[1]*Math.PI/180, r[2]*Math.PI/180);
      mesh.scale.set(s[0],s[1],s[2]);
      const nm=obj.name||type;
      nameCnt[type]=(nameCnt[type]||0)+1;
      mesh.userData={{type, name:nm, layer:'Layer 0', note:obj.note||''}};
      scene.add(mesh); objects.push(mesh);
      objMeta.set(mesh,{{bbox:null,dimGrp:null,normHelper:null,history:['ai_generated',...(obj.operations||[])]}});
      built.push(obj.name+' ('+type+')');
    }}
    updObjCount();
    // Frame the scene
    orb.r=30; orb.tx=0; orb.ty=3; orb.tz=0;

    // Show summary
    const html='<div class="ai-tag">'+design.name+'</div>'
      +'<p style="margin-bottom:8px;color:#5090b0;">'+design.description+'</p>'
      +'<div class="ai-sec">Parts ('+built.length+')</div>'
      +'<ul style="padding-left:14px;margin:4px 0;">'
      +built.map(b=>'<li style="margin:2px 0;color:#3a7090;">'+b+'</li>').join('')
      +'</ul>'
      +'<div class="ai-sec">Design Notes</div>'
      +'<p style="color:#4a7a9a;">'+design.notes+'</p>'
      +(design.objects||[]).filter(o=>o.note).length?
        '<div class="ai-sec">Part Notes</div>'
        +(design.objects||[]).filter(o=>o.note).map(o=>
          '<div class="pr" style="margin:3px 0;"><span class="pl">'+o.name+'</span>'
          +'<span class="pv" style="font-size:9px;color:#2a5070;">'+o.note+'</span></div>'
        ).join('') : '';
    body.innerHTML=html;
    setMsg('Generated: '+design.name+' — '+built.length+' parts · click parts to select');
  }} catch(err){{
    body.innerHTML='<div style="color:#cc4444;font-size:11px;">✗ Network error: '+err.message+'</div>';
    setMsg('Network error'); console.error(err);
  }}
}}

// ══════════════════════════════════════════════════════════════
// ── AI ANALYZER ──────────────────────────────────────────────
// ══════════════════════════════════════════════════════════════
async function analyzeSelected(){{
  if(!selected) return setMsg('Select an object first, then press X');
  if(!OPENROUTER_API_KEY) return setMsg('No API key — add OPENROUTER_API_KEY to secrets.toml');

  const panel=document.getElementById('ai-analyze-panel');
  const body=document.getElementById('ai-analyze-body');
  panel.style.display='flex';
  body.innerHTML='<div class="ldg"><span>Analyzing</span><span class="dot">■</span><span class="dot">■</span><span class="dot">■</span></div>';

  const bb=new THREE.Box3().setFromObject(selected);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  const ctr=new THREE.Vector3(); bb.getCenter(ctr);
  const c=selected.material.color;
  const m=objMeta.get(selected);

  const allObjs=objects.map(o=>{{
    const ob=new THREE.Box3().setFromObject(o);
    const os=new THREE.Vector3(); ob.getSize(os);
    return o.userData.name+'('+o.userData.type+') at '+o.position.toArray().map(v=>v.toFixed(2)).join(',');
  }}).join('; ');

  const modeMap={{
    'General Design Review':'Give a concise engineering design review covering geometry, placement, proportions, and role in the assembly.',
    'Structural Analysis':'Analyze structural properties: stress points, weak regions, support requirements, load paths, and recommended improvements.',
    'Dimensional Check':'Review proportions and flag non-standard dimensions. Suggest real-world standard sizes.',
    'GD&T Suggestions':'Suggest GD&T annotations: datum references, form tolerances, position tolerances.',
    'Manufacturing Feasibility':'Assess manufacturability: draft angles, undercuts, wall thickness, recommended processes (casting, milling, printing).',
    'FEA Pre-check':'Identify mesh refinement regions, boundary condition locations, and element type recommendations.',
    'Assembly Notes':'Describe how this part interfaces with adjacent objects. Suggest mate types, fits, and assembly sequence.',
  }};

  const prompt=`You are a senior mechanical engineer reviewing a CAD model part.

SELECTED OBJECT:
  Name: ${{selected.userData.name}}
  Type: ${{selected.userData.type}}
  Layer: ${{selected.userData.layer||'Layer 0'}}
  Position: X=${{selected.position.x.toFixed(3)}} Y=${{selected.position.y.toFixed(3)}} Z=${{selected.position.z.toFixed(3)}}
  Rotation: Rx=${{(selected.rotation.x*57.3).toFixed(1)}}° Ry=${{(selected.rotation.y*57.3).toFixed(1)}}° Rz=${{(selected.rotation.z*57.3).toFixed(1)}}°
  Bounding box: ${{sz.x.toFixed(3)}} × ${{sz.y.toFixed(3)}} × ${{sz.z.toFixed(3)}} units
  Volume (bbox): ${{(sz.x*sz.y*sz.z).toFixed(4)}} u³
  Color: #${{c.getHexString()}}
  Roughness: ${{selected.material.roughness?.toFixed(3)}}
  Metalness: ${{selected.material.metalness?.toFixed(3)}}
  CAD history: ${{(m?.history||[]).join(' → ')}}
  Note: ${{selected.userData.note||'none'}}

SCENE (${{objects.length}} objects): ${{allObjs}}

TASK: ${{modeMap[ANALYSIS_MODE]||modeMap['General Design Review']}}
${{AI_DETAIL==='detailed'?'Provide 4-6 paragraphs with sub-sections.':'Be concise — 2-3 paragraphs.'}}
Reference actual object name and numerical properties.`;

  try{{
    const resp=await fetch('https://openrouter.ai/api/v1/chat/completions',{{
      method:'POST',
      headers:{{
        'Authorization':'Bearer '+OPENROUTER_API_KEY,
        'Content-Type':'application/json',
        'HTTP-Referer':'https://ai-cad-studio.streamlit.app',
        'X-Title':'AI CAD Studio Pro',
      }},
      body:JSON.stringify({{
        model:OPENROUTER_API_KEY?'{OPENROUTER_MODEL}':'anthropic/claude-haiku-4-5',
        max_tokens:AI_DETAIL==='detailed'?900:450,
        temperature:0.3,
        messages:[{{role:'user',content:prompt}}],
      }}),
    }});
    const data=await resp.json();
    if(!resp.ok){{
      body.innerHTML='<div class="ai-tag">'+selected.userData.name+'</div>'
        +'<div style="color:#cc4444;font-size:11px;">✗ Error '+resp.status+': '+(data.error?.message||resp.statusText)+'</div>';
      return setMsg('Analyze error '+resp.status);
    }}
    const text=data.choices?.[0]?.message?.content||'(no response)';
    const fmt=text.split('\\n').filter(l=>l.trim()).map(l=>{{
      if(l.match(/^#+\\s/)) return '<div class="ai-sec">'+l.replace(/^#+\\s/,'')+'</div>';
      if(l.match(/^\\*\\*(.+)\\*\\*/)) return '<div class="ai-sec">'+l.replace(/\\*\\*/g,'')+'</div>';
      return '<p style="margin-bottom:8px">'+l+'</p>';
    }}).join('');
    body.innerHTML='<div class="ai-tag">'+selected.userData.name+' · '+ANALYSIS_MODE+'</div>'+fmt;
    setMsg('Analysis complete for '+selected.userData.name);
  }} catch(err){{
    body.innerHTML='<div style="color:#cc4444;font-size:11px;">✗ '+err.message+'</div>';
    setMsg('Network error'); console.error(err);
  }}
}}

// ══════════════════════════════════════════════════════════════
// ── MEASUREMENT TOOL ─────────────────────────────────────────
// ══════════════════════════════════════════════════════════════
function doMeasureClick(ev){{
  const hits=getHits(ev,[...objects,gndMesh]);
  if(!hits.length) return;
  let pt=hits[0].point.clone();
  if(cadSt.snapGrid){{
    pt.x=Math.round(pt.x/cadSt.snapSize)*cadSt.snapSize;
    pt.z=Math.round(pt.z/cadSt.snapSize)*cadSt.snapSize;
  }}
  cadSt.measurePts.push(pt);
  if(cadSt.measurePts.length===1){{
    document.getElementById('mp-txt').textContent=
      'P1=('+pt.x.toFixed(2)+', '+pt.y.toFixed(2)+', '+pt.z.toFixed(2)+') — click 2nd point';
    setMsg('Measure P1 set');
  }}
  if(cadSt.measurePts.length===2){{
    const [p1,p2]=cadSt.measurePts;
    const dist=p1.distanceTo(p2);
    const dx=Math.abs(p2.x-p1.x), dy=Math.abs(p2.y-p1.y), dz=Math.abs(p2.z-p1.z);
    if(cadSt.measureLine) scene.remove(cadSt.measureLine);
    const geo=new THREE.BufferGeometry().setFromPoints([p1,p2]);
    cadSt.measureLine=new THREE.Line(geo,
      new THREE.LineDashedMaterial({{color:0x30d0f0,dashSize:0.14,gapSize:0.07,depthTest:false}}));
    cadSt.measureLine.computeLineDistances();
    scene.add(cadSt.measureLine);
    document.getElementById('mp-txt').textContent=
      'Δ='+dist.toFixed(4)+' | X='+dx.toFixed(3)+' Y='+dy.toFixed(3)+' Z='+dz.toFixed(3);
    document.getElementById('sb-dist').textContent='DIST:'+dist.toFixed(4)+'u';
    cadSt.measurePts=[];
    setMsg('Measurement: '+dist.toFixed(4)+' units');
  }}
}}

// ══════════════════════════════════════════════════════════════
// ── RAYCASTER ────────────────────────────────────────────────
// ══════════════════════════════════════════════════════════════
const _ray=new THREE.Raycaster();
const _mv=new THREE.Vector2();
function getHits(ev, targets){{
  const rc=renderer.domElement.getBoundingClientRect();
  _mv.x=((ev.clientX-rc.left)/rc.width)*2-1;
  _mv.y=-((ev.clientY-rc.top)/rc.height)*2+1;
  _ray.setFromCamera(_mv,cam);
  return _ray.intersectObjects(targets,true);
}}

// ══════════════════════════════════════════════════════════════
// ── MOUSE / POINTER ──────────────────────────────────────────
// ══════════════════════════════════════════════════════════════
let isOrb=false, isPan=false, isDrag=false;
let lm={{x:0,y:0}}, dm={{x:0,y:0}};
let dragAxis=null, sp0=null, sr0=null, ss0=null;
let ptrMoved=false;

renderer.domElement.addEventListener('mousedown', e=>{{
  dm={{x:e.clientX,y:e.clientY}}; ptrMoved=false;
  if(selected&&gizmoGroup&&!cadSt.measureMode&&cadSt.operationMode===null){{
    const all=[]; gizmoGroup.traverse(c=>{{if(c.isMesh||c.isLine)all.push(c);}});
    const hits=getHits(e,all);
    if(hits.length){{
      let anc=hits[0].object;
      while(anc.parent&&!anc.userData.axis) anc=anc.parent;
      if(anc.userData.axis){{
        dragAxis=anc.userData.axis; isDrag=true;
        sp0=selected.position.clone(); sr0=selected.rotation.clone(); ss0=selected.scale.clone();
        lm={{x:e.clientX,y:e.clientY}}; return;
      }}
    }}
  }}
  if(e.button===0) isOrb=true;
  if(e.button===2) isPan=true;
  lm={{x:e.clientX,y:e.clientY}};
}});

renderer.domElement.addEventListener('mouseup', e=>{{
  if(isDrag){{ isDrag=false; dragAxis=null; updateAllBboxes(); updatePropsPanel(selected); pushHistory(selected,transformMode); return; }}
  isOrb=false; isPan=false;
  if(!ptrMoved&&Math.abs(e.clientX-dm.x)<6&&Math.abs(e.clientY-dm.y)<6&&e.button===0){{
    if(cadSt.measureMode){{ doMeasureClick(e); return; }}
    const hits=getHits(e,objects);
    const hit=hits.length?hits[0].object:null;

    if(cadSt.operationMode==='loft-select'){{
      if(hit&&!cadSt.loftTargets.includes(hit)){{
        cadSt.loftTargets.push(hit);
        hit.material.emissive?.setHex(0x0d2840);
        setMsg('LOFT: '+cadSt.loftTargets.length+'/2 profiles selected'+(cadSt.loftTargets.length===2?' — executing…':''));
        if(cadSt.loftTargets.length===2) setTimeout(finishLoft,100);
      }}
      return;
    }}
    if(cadSt.operationMode&&cadSt.operationMode.startsWith('boolean-')){{
      const op=cadSt.operationMode.split('-')[1];
      if(hit&&hit!==cadSt.booleanTarget){{
        finishBoolean(op,cadSt.booleanTarget,hit);
      }}
      return;
    }}
    selectObj(hit);
  }}
}});

renderer.domElement.addEventListener('mousemove', e=>{{
  if(Math.abs(e.clientX-dm.x)>4||Math.abs(e.clientY-dm.y)>4) ptrMoved=true;

  // Cursor world pos
  const hits=getHits(e,[...objects,gndMesh]);
  if(hits.length){{
    const hp=hits[0].point;
    let cx=hp.x, cy=hp.y, cz=hp.z;
    if(cadSt.snapGrid){{
      cx=Math.round(cx/cadSt.snapSize)*cadSt.snapSize;
      cz=Math.round(cz/cadSt.snapSize)*cadSt.snapSize;
      const sd=document.getElementById('snap-dot');
      sd.style.display='block'; sd.style.left=e.clientX+'px'; sd.style.top=e.clientY+'px';
    }} else document.getElementById('snap-dot').style.display='none';
    document.getElementById('hud-cur').textContent=cx.toFixed(2)+', '+cy.toFixed(2)+', '+cz.toFixed(2);
  }}

  if(isDrag&&selected&&dragAxis){{
    const dx=(e.clientX-lm.x)*0.018, dy=-(e.clientY-lm.y)*0.018;
    const d=Math.abs(dx)>Math.abs(dy)?dx:dy;
    const ax=dragAxis;
    const snap=cadSt.snapGrid?cadSt.snapSize:null;
    const sn=v=>snap?Math.round(v/snap)*snap:v;
    if(transformMode==='move'){{
      const np=sp0.clone();
      if(ax==='x') np.x=sn(sp0.x+dx*2.5);
      else if(ax==='y') np.y=sn(sp0.y+dy*2.5);
      else if(ax==='z') np.z=sn(sp0.z+dx*2.5);
      else if(ax==='xz'){{np.x=sn(sp0.x+dx*2.5);np.z=sn(sp0.z+dx*2.5);}}
      else if(ax==='xy'){{np.x=sn(sp0.x+dx*2.5);np.y=sn(sp0.y+dy*2.5);}}
      else if(ax==='yz'){{np.y=sn(sp0.y+dy*2.5);np.z=sn(sp0.z+dx*2.5);}}
      selected.position.copy(np);
    }} else if(transformMode==='rotate'){{
      const nr=sr0.clone();
      if(ax==='x') nr.x=sr0.x+d*2.8;
      else if(ax==='y') nr.y=sr0.y+d*2.8;
      else nr.z=sr0.z+d*2.8;
      selected.rotation.copy(nr);
    }} else {{
      const sc=ss0.clone(), f=1+d*1.4;
      if(ax==='xyz'){{sc.x=Math.max(0.01,ss0.x*f);sc.y=Math.max(0.01,ss0.y*f);sc.z=Math.max(0.01,ss0.z*f);}}
      else if(ax==='x') sc.x=Math.max(0.01,ss0.x*f);
      else if(ax==='y') sc.y=Math.max(0.01,ss0.y*f);
      else sc.z=Math.max(0.01,ss0.z*f);
      selected.scale.copy(sc);
    }}
    syncGizmo(); updateHUD();
    lm={{x:e.clientX,y:e.clientY}}; return;
  }}
  if(isOrb){{
    orb.theta-=(e.clientX-lm.x)*0.006;
    orb.phi-=(e.clientY-lm.y)*0.006;
    orb.phi=Math.max(0.04,Math.min(Math.PI-0.04,orb.phi));
  }}
  if(isPan){{
    const spd=0.009*(orb.r/10);
    const fwd=new THREE.Vector3(orb.tx-cam.position.x,0,orb.tz-cam.position.z).normalize();
    const right=new THREE.Vector3().crossVectors(fwd,new THREE.Vector3(0,1,0)).normalize();
    orb.tx-=right.x*(e.clientX-lm.x)*spd;
    orb.tz-=right.z*(e.clientX-lm.x)*spd;
    orb.ty+=(e.clientY-lm.y)*spd;
  }}
  lm={{x:e.clientX,y:e.clientY}};
}});

renderer.domElement.addEventListener('wheel', e=>{{
  if(cadSt.sectionMode&&e.ctrlKey){{
    cadSt.sectionY+=e.deltaY*0.004;
    cadSt.clippingPlane.constant=cadSt.sectionY;
    setMsg('Section Y='+cadSt.sectionY.toFixed(2)); return;
  }}
  orb.r*=1+e.deltaY*0.0007;
  orb.r=Math.max(1,Math.min(500,orb.r));
}},{{passive:true}});

renderer.domElement.addEventListener('contextmenu',e=>e.preventDefault());

// ── Keyboard ──────────────────────────────────────────────────
document.addEventListener('keydown',e=>{{
  if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA') return;
  const k=e.key.toLowerCase();
  if(k==='x'&&!e.ctrlKey) analyzeSelected();
  if(k==='e'&&!e.ctrlKey) cadExtrude(2.0);
  if(k==='escape'){{ closeGen();closeAnalyze();selectObj(null);cadSt.operationMode=null;cadSt.loftTargets=[];setOpOverlay(null); }}
  if(k==='delete'||k==='backspace'){{ e.preventDefault();deleteSel(); }}
  if(k==='d'&&!e.ctrlKey) duplicate();
  if(k==='f') frameSelected();
  if(k==='g') toggleSnap();
  if(k==='w') toggleWire();
  if(k==='m') toggleMeasure();
}});

// ── Status helper ─────────────────────────────────────────────
function setMsg(msg){{ document.getElementById('sb-msg').textContent=msg; }}

// ── Command router (from Python sidebar) ─────────────────────
(function(){{
  const cmd={js_cmd};
  if(!cmd||cmd==='null') return;
  if(cmd.startsWith('prim:'))         {{ addPrim(cmd.slice(5)); return; }}
  if(cmd==='scene:delete')            {{ deleteSel(); return; }}
  if(cmd==='scene:duplicate')         {{ duplicate(); return; }}
  if(cmd==='scene:clear')             {{ clearScene(); return; }}
  if(cmd.startsWith('mat:apply:'))    {{ const p=cmd.split(':'); applyMat(p[2],p[3],p[4],p[5],p[6]); return; }}
  if(cmd.startsWith('xform:pos:'))    {{ const p=cmd.split(':'); applyPos(p[2],p[3],p[4]); return; }}
  if(cmd.startsWith('xform:rot:'))    {{ const p=cmd.split(':'); applyRot(parseFloat(p[2]),parseFloat(p[3]),parseFloat(p[4])); return; }}
  if(cmd.startsWith('xform:scale:'))  {{ const p=cmd.split(':'); applyScale(p[2],p[3],p[4]); return; }}
  if(cmd.startsWith('cad:extrude:'))  {{ cadExtrude(parseFloat(cmd.split(':')[2])); return; }}
  if(cmd==='cad:revolve')             {{ cadRevolve(); return; }}
  if(cmd==='cad:loft')                {{ startLoft(); return; }}
  if(cmd.startsWith('cad:shell:'))    {{ cadShell(parseFloat(cmd.split(':')[2])); return; }}
  if(cmd==='cad:mirror')              {{ cadMirror('X'); return; }}
  if(cmd.startsWith('cad:array:'))    {{ const p=cmd.split(':'); cadArray(parseInt(p[2]),parseFloat(p[3]),p[4],p[5]); return; }}
  if(cmd==='cad:boolean:union')       {{ if(selected)startBoolean('union'); else setMsg('Select first object for union'); return; }}
  if(cmd==='cad:boolean:subtract')    {{ if(selected)startBoolean('subtract'); else setMsg('Select first object for subtract'); return; }}
  if(cmd==='view:wire')               {{ toggleWire(); return; }}
  if(cmd==='view:bbox')               {{ toggleBbox(); return; }}
  if(cmd==='view:dims')               {{ toggleDims(); return; }}
  if(cmd==='view:normals')            {{ toggleNormals(); return; }}
  if(cmd==='view:snap')               {{ toggleSnap(); return; }}
  if(cmd==='view:axes')               {{ toggleAxes(); return; }}
  if(cmd==='view:measure')            {{ toggleMeasure(); return; }}
  if(cmd==='view:section')            {{ toggleSection(); return; }}
  if(cmd.startsWith('layer:vis:'))    {{ layerVis(cmd.slice(10)); return; }}
  if(cmd.startsWith('layer:lock:'))   {{ layerLock(cmd.slice(11)); return; }}
  if(cmd.startsWith('view:preset:'))  {{ setView(cmd.slice(12)); return; }}
}})();

// ── AI Generator auto-run if payload provided ─────────────────
(function(){{
  if(!GEN_PAYLOAD) return;
  try{{
    const payload=JSON.parse(GEN_PAYLOAD);
    if(payload.prompt&&payload.apiKey) runAIGenerator(payload);
    else if(payload.prompt&&!payload.apiKey){{
      const p=document.getElementById('ai-gen-panel');
      const b=document.getElementById('ai-gen-body');
      p.style.display='flex';
      b.innerHTML='<div style="color:#cc4444;font-size:11px;">✗ No API key — add OPENROUTER_API_KEY to secrets.toml</div>';
    }}
  }} catch(e){{}}
}})();

// ── Render loop ───────────────────────────────────────────────
(function animate(){{
  requestAnimationFrame(animate);
  applyOrbit();
  if(selected&&gizmoGroup) syncGizmo();
  updateAllBboxes();
  updateHUD();
  renderer.render(scene,cam);
}})();

onResize();
</script>
</body>
</html>"""

st.markdown("## 📐 AI CAD Studio Pro")
components.html(HTML, height=740, scrolling=False)
st.caption(
    "**AI Generator:** describe any design → Generate · "
    "**CAD Ops:** Extrude / Revolve / Shell / Loft / Mirror / Array / Boolean · "
    "**Keys:** [E] extrude · [X] analyze · [F] frame · [G] snap · [W] wire · [M] measure · [D] dup · [Del] delete"
)