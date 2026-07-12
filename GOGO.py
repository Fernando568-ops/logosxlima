import streamlit as st
import streamlit.components.v1 as components
import json

try:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
except (KeyError, FileNotFoundError):
    OPENROUTER_API_KEY = ""

try:
    OPENROUTER_MODEL_DEFAULT = st.secrets.get("OPENROUTER_MODEL", "anthropic/claude-haiku-4-5")
except Exception:
    OPENROUTER_MODEL_DEFAULT = "anthropic/claude-haiku-4-5"

st.set_page_config(page_title="AI CAD Studio Pro", layout="wide", page_icon="📐")

st.markdown("""
<style>
body, .stApp { background:#060a0f !important; color:#c8d8e8; }
footer, header, #MainMenu { visibility:hidden; }
.block-container { padding:0 !important; margin:0 !important; max-width:100% !important; }
iframe { border:none !important; }
</style>
""", unsafe_allow_html=True)

# The entire app lives in one HTML page.
# Streamlit only serves it once. All state lives in JS.
# Sidebar buttons in the iframe communicate internally — no Python reruns needed.
HTML = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>AI CAD Studio Pro</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:100%;height:100%;overflow:hidden;background:#060a0f;
  font-family:'Courier New',monospace;color:#c8d8e8;user-select:none;}

/* ── Layout ── */
#sidebar{
  position:fixed;top:0;left:0;width:240px;height:100%;
  background:#07090e;border-right:1px solid #14202c;
  overflow-y:auto;overflow-x:hidden;z-index:100;
  display:flex;flex-direction:column;
}
#sidebar::-webkit-scrollbar{width:4px;}
#sidebar::-webkit-scrollbar-track{background:#060a0f;}
#sidebar::-webkit-scrollbar-thumb{background:#1a2a3a;border-radius:2px;}

#viewport{position:fixed;top:0;left:240px;right:0;bottom:0;}
canvas{display:block;width:100%!important;height:100%!important;}

/* ── Sidebar sections ── */
.sb-title{
  padding:10px 12px 6px;font-size:13px;color:#4a8ac0;
  border-bottom:1px solid #10202c;letter-spacing:.05em;
  display:flex;align-items:center;gap:6px;
}
.sb-section{margin:0;padding:0;}
.sb-label{
  padding:5px 10px 2px;font-size:9px;color:#1e3a54;
  text-transform:uppercase;letter-spacing:.1em;
}
.sb-row{display:flex;gap:2px;padding:1px 6px;}
.sb-row.col1{padding:1px 6px;}
.sb-sep{height:1px;background:#0e1c28;margin:4px 0;}

/* ── Buttons ── */
button{
  background:#0a1420;color:#6a8aaa;border:1px solid #14202c;
  border-radius:3px;font-size:10px;padding:4px 6px;cursor:pointer;
  font-family:'Courier New',monospace;transition:all .1s;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}
button:hover{background:#142840;border-color:#2a5a8a;color:#90c0e0;}
button.active{background:#0a2040;border-color:#2060a0;color:#60a0d0;}
button.warn{background:#201000;border-color:#604000;color:#c08030;}
button.full{width:100%;}
button.half{flex:1;}
button.third{flex:1;}

/* ── Inputs ── */
input[type=text],input[type=number],select,textarea{
  background:#070b12;color:#7aaace;border:1px solid #14202c;
  border-radius:3px;font-size:10px;padding:3px 6px;width:100%;
  font-family:'Courier New',monospace;outline:none;
}
input[type=range]{width:100%;accent-color:#2a6aaa;height:3px;}
input[type=color]{width:32px;height:22px;border:1px solid #14202c;
  border-radius:3px;background:none;padding:0;cursor:pointer;}
select{cursor:pointer;}
textarea{resize:none;height:60px;line-height:1.5;}

.input-row{
  display:flex;align-items:center;gap:4px;padding:1px 6px;
}
.input-row label{font-size:9px;color:#1e3a54;min-width:28px;}
.xyz-row{display:flex;gap:2px;padding:1px 6px;}
.xyz-row input{text-align:center;}

/* ── Status bar ── */
#statusbar{
  position:fixed;bottom:0;left:240px;right:0;height:22px;
  background:#040810ee;border-top:1px solid #0e1820;
  display:flex;align-items:center;font-size:10px;color:#2a4060;z-index:50;
}
.sc{padding:0 8px;height:100%;display:flex;align-items:center;border-right:1px solid #0a1420;}
.sc.on{color:#3a8ad0;}.sc.warn{color:#c08030;}
#sb-msg{flex:1;padding:0 8px;}
#sb-dist{min-width:120px;padding:0 8px;text-align:right;}

/* ── HUD ── */
#hud{
  position:fixed;top:8px;left:252px;
  background:#04080ccc;border:1px solid #14202c;border-radius:3px;
  padding:5px 10px;font-size:10px;line-height:1.9;
  pointer-events:none;min-width:210px;z-index:50;
}
#hud .v{color:#3a7aaa;}#hud .h{color:#1a3a5a;}
#hud .sel-head{color:#4a90d0;font-size:11px;border-top:1px solid #14202c;
  margin-top:3px;padding-top:3px;}

/* ── Props panel ── */
#props{
  position:fixed;top:8px;right:8px;width:190px;
  background:#04080cee;border:1px solid #14202c;border-radius:3px;
  display:none;font-size:10px;z-index:50;
}
.ph-hdr{padding:5px 8px;border-bottom:1px solid #0e1820;color:#1e5080;
  font-size:9px;text-transform:uppercase;letter-spacing:.08em;
  display:flex;justify-content:space-between;}
#props-body{padding:6px 8px;}
.pr{display:flex;justify-content:space-between;margin:2px 0;}
.pl{color:#1a3a56;}.pv{color:#3a7ab8;font-family:monospace;}
.ph{color:#0e2030;text-transform:uppercase;font-size:8px;letter-spacing:.06em;
  margin:5px 0 2px;border-bottom:1px solid #0e1820;padding-bottom:1px;}

/* ── Measure overlay ── */
#measure-panel{
  position:fixed;top:8px;left:50%;transform:translateX(-50%);
  background:#020e1aee;border:1px solid #144060;border-radius:3px;
  padding:4px 14px;font-size:11px;color:#28b0e0;display:none;
  pointer-events:none;text-align:center;white-space:nowrap;z-index:51;
}

/* ── Op overlay ── */
#op-overlay{
  position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
  background:#020a14cc;border:1px solid #164060;border-radius:4px;
  padding:10px 22px;font-size:12px;color:#2898d0;
  pointer-events:none;display:none;text-align:center;z-index:52;
}

/* ── AI panels ── */
.ai-panel{
  position:fixed;bottom:28px;right:8px;width:360px;
  background:#030810f4;border:1px solid #14202c;border-radius:3px;
  display:none;flex-direction:column;max-height:52vh;
  box-shadow:0 4px 28px #00000099;z-index:60;
}
.ai-hdr{
  display:flex;align-items:center;justify-content:space-between;
  padding:6px 10px;border-bottom:1px solid #0e1820;
}
.ai-hdr span{color:#2a6aaa;font-size:9px;letter-spacing:.1em;text-transform:uppercase;}
.ai-close{background:none;border:none;color:#1e3a5a;cursor:pointer;font-size:13px;padding:0 3px;}
.ai-close:hover{color:#e0e8f0;}
.ai-body{padding:10px;overflow-y:auto;flex:1;font-size:11px;color:#6090b0;line-height:1.8;}
.ai-tag{background:#081820;border:1px solid #143050;border-radius:2px;
  padding:2px 7px;font-size:9px;color:#286090;margin-bottom:6px;display:inline-block;
  text-transform:uppercase;letter-spacing:.06em;}
.ai-sec{color:#1a5a7a;font-size:9px;text-transform:uppercase;letter-spacing:.07em;
  margin:7px 0 2px;border-bottom:1px solid #0e1820;padding-bottom:1px;}
.ldg{display:flex;align-items:center;gap:6px;color:#1e3a5a;}
.dot{animation:blink 1.4s infinite;}
.dot:nth-child(2){animation-delay:.2s;}.dot:nth-child(3){animation-delay:.4s;}
@keyframes blink{0%,80%,100%{opacity:0;}40%{opacity:1;}}
#snap-dot{position:fixed;width:7px;height:7px;background:#30d030;border-radius:50%;
  pointer-events:none;display:none;transform:translate(-3px,-3px);z-index:55;}
</style>
</head>
<body>

<!-- ══════════════ SIDEBAR ══════════════ -->
<div id="sidebar">
  <div class="sb-title">📐 AI CAD Studio Pro</div>

  <!-- API Status -->
  <div id="api-status" style="padding:4px 8px;font-size:10px;"></div>

  <!-- AI Generator -->
  <div class="sb-section">
    <div class="sb-label">✦ AI Design Generator</div>
    <div style="padding:2px 6px;">
      <textarea id="ai-prompt" placeholder="e.g. suspension bridge with two towers, gear assembly, office chair, wind turbine..."></textarea>
    </div>
    <div class="sb-row">
      <select id="ai-model" class="half" style="flex:1">
        <option value="anthropic/claude-haiku-4-5">claude-haiku-4-5 (fast)</option>
        <option value="anthropic/claude-3-haiku">claude-3-haiku (cheap)</option>
        <option value="anthropic/claude-3.5-haiku">claude-3.5-haiku</option>
        <option value="anthropic/claude-3.5-sonnet">claude-3.5-sonnet</option>
        <option value="openai/gpt-4o-mini">gpt-4o-mini</option>
        <option value="google/gemini-flash-1.5">gemini-flash-1.5</option>
        <option value="mistralai/mistral-7b-instruct">mistral-7b</option>
      </select>
    </div>
    <div class="sb-row" style="padding:2px 6px;">
      <button class="full" onclick="runGenerator()" style="background:#081e30;border-color:#144060;color:#40a0d0;">
        ✦ Generate Design
      </button>
    </div>
  </div>
  <div class="sb-sep"></div>

  <!-- Primitives -->
  <div class="sb-section">
    <div class="sb-label">➕ Primitives</div>
    <div class="sb-row">
      <button class="third" onclick="addPrim('box')">⬛ Box</button>
      <button class="third" onclick="addPrim('sphere')">● Sphere</button>
      <button class="third" onclick="addPrim('cylinder')">⬤ Cyl</button>
    </div>
    <div class="sb-row">
      <button class="third" onclick="addPrim('cone')">▲ Cone</button>
      <button class="third" onclick="addPrim('torus')">⭕ Torus</button>
      <button class="third" onclick="addPrim('wedge')">◤ Wedge</button>
    </div>
    <div class="sb-row">
      <button class="third" onclick="addPrim('plane')">▭ Plane</button>
      <button class="third" onclick="addPrim('pipe')">| Pipe</button>
      <button class="third" onclick="addPrim('spring')">~ Spring</button>
    </div>
  </div>
  <div class="sb-sep"></div>

  <!-- Transform -->
  <div class="sb-section">
    <div class="sb-label">🎮 Transform Mode</div>
    <div class="sb-row">
      <button class="third active" id="btn-move"   onclick="setTransformMode('move')">Move</button>
      <button class="third"        id="btn-rotate" onclick="setTransformMode('rotate')">Rotate</button>
      <button class="third"        id="btn-scale"  onclick="setTransformMode('scale')">Scale</button>
    </div>
    <div class="sb-row">
      <button class="half active" id="btn-world" onclick="setSpace('world')">World</button>
      <button class="half"        id="btn-local" onclick="setSpace('local')">Local</button>
    </div>

    <div class="sb-label" style="margin-top:4px;">Precise Position (X / Y / Z)</div>
    <div class="xyz-row">
      <input type="number" id="in-px" value="0" step="0.25" onchange="applyPos()">
      <input type="number" id="in-py" value="0" step="0.25" onchange="applyPos()">
      <input type="number" id="in-pz" value="0" step="0.25" onchange="applyPos()">
    </div>
    <div class="sb-label">Rotation (°) X / Y / Z</div>
    <div class="xyz-row">
      <input type="number" id="in-rx" value="0" step="15" onchange="applyRot()">
      <input type="number" id="in-ry" value="0" step="15" onchange="applyRot()">
      <input type="number" id="in-rz" value="0" step="15" onchange="applyRot()">
    </div>
    <div class="sb-label">Scale X / Y / Z</div>
    <div class="xyz-row">
      <input type="number" id="in-sx" value="1" step="0.1" min="0.001" onchange="applyScale()">
      <input type="number" id="in-sy" value="1" step="0.1" min="0.001" onchange="applyScale()">
      <input type="number" id="in-sz" value="1" step="0.1" min="0.001" onchange="applyScale()">
    </div>
  </div>
  <div class="sb-sep"></div>

  <!-- CAD Operations -->
  <div class="sb-section">
    <div class="sb-label">⚙️ CAD Operations</div>
    <div class="input-row">
      <label>Depth</label>
      <input type="range" id="ext-depth" min="0.1" max="15" value="2" step="0.1"
        oninput="document.getElementById('ext-depth-val').textContent=parseFloat(this.value).toFixed(1)">
      <span id="ext-depth-val" style="font-size:10px;color:#2a6090;min-width:28px;">2.0</span>
    </div>
    <div class="sb-row">
      <button class="half" onclick="cadExtrude()">↑ Extrude</button>
      <button class="half" onclick="cadRevolve()">↻ Revolve</button>
    </div>
    <div class="input-row">
      <label>Shell</label>
      <input type="range" id="shell-t" min="0.02" max="2" value="0.15" step="0.01"
        oninput="document.getElementById('shell-tv').textContent=parseFloat(this.value).toFixed(2)">
      <span id="shell-tv" style="font-size:10px;color:#2a6090;min-width:28px;">0.15</span>
    </div>
    <div class="sb-row">
      <button class="half" onclick="cadShell()">□ Shell</button>
      <button class="half" onclick="cadMirror('X')">⟺ Mirror X</button>
    </div>
    <div class="input-row">
      <label>Arr#</label>
      <input type="number" id="arr-n" value="3" min="2" max="24" style="width:48px;">
      <label style="margin-left:4px;">Sp</label>
      <input type="number" id="arr-sp" value="2.5" step="0.5" style="width:48px;">
    </div>
    <div class="sb-row">
      <select id="arr-ax" class="third"><option>X</option><option>Y</option><option>Z</option></select>
      <select id="arr-ty" class="third"><option>Linear</option><option>Radial</option></select>
      <button class="third" onclick="cadArray()">⊞ Array</button>
    </div>
    <div class="sb-row">
      <button class="half" onclick="startLoft()">◇ Loft</button>
      <button class="half" onclick="startBoolean('union')">∪ Union</button>
    </div>
    <div class="sb-row">
      <button class="half" onclick="startBoolean('subtract')">∖ Subtract</button>
      <button class="half" onclick="cadFillet()">⌒ Fillet</button>
    </div>
  </div>
  <div class="sb-sep"></div>

  <!-- View -->
  <div class="sb-section">
    <div class="sb-label">👁 View</div>
    <div class="sb-row">
      <button class="half" id="btn-wire" onclick="toggleWire()">⬡ Wire</button>
      <button class="half" id="btn-bbox" onclick="toggleBbox()">⬜ BBox</button>
    </div>
    <div class="sb-row">
      <button class="half" id="btn-dims" onclick="toggleDims()">↔ Dims</button>
      <button class="half" id="btn-axes" onclick="toggleAxes()">+ Axes</button>
    </div>
    <div class="sb-row">
      <button class="half" id="btn-measure" onclick="toggleMeasure()">📐 Measure</button>
      <button class="half" id="btn-section" onclick="toggleSection()">✂ Section</button>
    </div>
    <div class="input-row" id="section-ctrl" style="display:none">
      <label>SectY</label>
      <input type="range" id="sect-y" min="-5" max="10" value="2" step="0.1"
        oninput="moveSectionPlane(parseFloat(this.value))">
    </div>
    <div class="sb-row">
      <select id="view-preset" style="flex:1">
        <option>Perspective</option><option>Top</option>
        <option>Front</option><option>Right</option><option>Isometric</option>
      </select>
      <button style="flex:0 0 auto;" onclick="setView(document.getElementById('view-preset').value)">Go</button>
    </div>
  </div>
  <div class="sb-sep"></div>

  <!-- Material -->
  <div class="sb-section">
    <div class="sb-label">🎨 Material</div>
    <div class="sb-row">
      <select id="mat-preset" style="flex:1" onchange="applyMatPreset(this.value)">
        <option>Custom</option><option>Steel</option><option>Aluminium</option>
        <option>Brass</option><option>Plastic</option><option>Concrete</option>
        <option>Wood</option><option>Glass</option>
      </select>
      <input type="color" id="mat-color" value="#4a9eff" oninput="applyMatCustom()">
    </div>
    <div class="input-row">
      <label>Rough</label>
      <input type="range" id="mat-rough" min="0" max="1" value="0.4" step="0.01" oninput="applyMatCustom()">
    </div>
    <div class="input-row">
      <label>Metal</label>
      <input type="range" id="mat-metal" min="0" max="1" value="0.2" step="0.01" oninput="applyMatCustom()">
    </div>
    <div class="input-row">
      <label>Alpha</label>
      <input type="range" id="mat-alpha" min="0.05" max="1" value="1" step="0.01" oninput="applyMatCustom()">
    </div>
  </div>
  <div class="sb-sep"></div>

  <!-- Layers -->
  <div class="sb-section">
    <div class="sb-label">🗂 Layers</div>
    <div class="sb-row">
      <select id="active-layer" style="flex:1">
        <option>Layer 0</option><option>Construction</option>
        <option>Hidden</option><option>Dimensions</option>
      </select>
    </div>
    <div class="sb-row">
      <button class="half" onclick="layerVis()">👁 Toggle</button>
      <button class="half" onclick="layerLock()">🔒 Lock</button>
    </div>
  </div>
  <div class="sb-sep"></div>

  <!-- Scene -->
  <div class="sb-section">
    <div class="sb-label">🗑 Scene</div>
    <div class="sb-row">
      <button class="third" onclick="duplicate()">⧉ Dup</button>
      <button class="third" onclick="frameSelected()">⊙ Frame</button>
      <button class="third warn" onclick="deleteSel()">🗑 Del</button>
    </div>
    <div class="sb-row">
      <button class="full warn" onclick="clearScene()">✕ Clear All</button>
    </div>
  </div>
  <div class="sb-sep"></div>

  <!-- AI Analyze -->
  <div class="sb-section">
    <div class="sb-label">🔬 AI Analyze [X]</div>
    <div class="sb-row">
      <select id="ai-mode" style="flex:1">
        <option>General Design Review</option>
        <option>Structural Analysis</option>
        <option>Dimensional Check</option>
        <option>GD&T Suggestions</option>
        <option>Manufacturing Feasibility</option>
        <option>FEA Pre-check</option>
        <option>Assembly Notes</option>
      </select>
    </div>
    <div class="sb-row">
      <button class="half active" id="btn-brief"    onclick="setDetail('brief')">Brief</button>
      <button class="half"        id="btn-detailed" onclick="setDetail('detailed')">Detailed</button>
    </div>
    <div class="sb-row">
      <button class="full" onclick="analyzeSelected()" style="background:#081e30;border-color:#144060;color:#40a0d0;">
        [X] Analyze Selected
      </button>
    </div>
    <div style="padding:4px 6px;font-size:9px;color:#1a3050;line-height:1.8;">
      [E] Extrude · [D] Dup · [F] Frame<br>
      [G] Snap · [W] Wire · [M] Measure<br>
      [Del] Delete · [Esc] Deselect
    </div>
  </div>
  <div style="height:30px;"></div><!-- bottom padding -->
</div>

<!-- ══════════════ VIEWPORT ══════════════ -->
<div id="viewport"></div>

<!-- ══════════════ OVERLAYS ══════════════ -->
<div id="statusbar">
  <div class="sc" id="sb-mode">NAVIGATE</div>
  <div class="sc" id="sb-snap">SNAP:OFF</div>
  <div class="sc" id="sb-wire">WIRE:OFF</div>
  <div class="sc" id="sb-objs">OBJS:0</div>
  <div class="sc" id="sb-msg" style="flex:1">Ready — add shapes or use AI Generator</div>
  <div class="sc" id="sb-dist"></div>
</div>

<div id="hud">
  <div><span class="h">CURSOR </span><span class="v" id="hud-cur">--</span></div>
  <div><span class="h">CAM    </span><span class="v" id="hud-cam">--</span></div>
  <div id="hud-sel" style="display:none">
    <div class="sel-head" id="hud-name"></div>
    <div><span class="h">POS  </span><span class="v" id="hud-pos"></span></div>
    <div><span class="h">SIZE </span><span class="v" id="hud-sz"></span></div>
    <div><span class="h">OPS  </span><span class="v" id="hud-ops" style="color:#1a4060;font-size:9px;"></span></div>
  </div>
</div>

<div id="props">
  <div class="ph-hdr"><span>Properties</span><span id="props-type" style="color:#144060"></span></div>
  <div id="props-body"></div>
</div>

<div id="measure-panel"><span id="mp-txt">Click first point</span></div>
<div id="op-overlay"></div>
<div id="snap-dot"></div>

<!-- AI Panels -->
<div class="ai-panel" id="ai-gen-panel">
  <div class="ai-hdr">
    <span>✦ AI Design Generator</span>
    <button class="ai-close" onclick="document.getElementById('ai-gen-panel').style.display='none'">✕</button>
  </div>
  <div class="ai-body" id="ai-gen-body"></div>
</div>

<div class="ai-panel" id="ai-analyze-panel">
  <div class="ai-hdr">
    <span>📐 Claude Analysis</span>
    <button class="ai-close" onclick="document.getElementById('ai-analyze-panel').style.display='none'">✕</button>
  </div>
  <div class="ai-body" id="ai-analyze-body"></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ═══════════════════════════════════════════════════
// CONFIG (injected server-side, read-only after load)
// ═══════════════════════════════════════════════════
const CFG = {
  apiKey: "REPLACE_API_KEY",
  modelDefault: "REPLACE_MODEL",
};
// Patch from Python
CFG.apiKey       = `""" + OPENROUTER_API_KEY + r"""`;
CFG.modelDefault = `""" + OPENROUTER_MODEL_DEFAULT + r"""`;

// Set API status badge
(function(){
  const el = document.getElementById('api-status');
  if(CFG.apiKey){
    el.innerHTML = '<div style="background:#081808;border:1px solid #1a4a1a;border-radius:3px;padding:3px 8px;color:#2a8a40;">✓ OpenRouter connected</div>';
    document.getElementById('ai-model').value = CFG.modelDefault;
  } else {
    el.innerHTML = '<div style="background:#180808;border:1px solid #4a1a1a;border-radius:3px;padding:3px 8px;color:#aa3030;">✗ Add OPENROUTER_API_KEY to secrets.toml</div>';
  }
})();

// ═══════════════════════════════════════════════════
// THREE.JS SETUP
// ═══════════════════════════════════════════════════
const vp = document.getElementById('viewport');

const renderer = new THREE.WebGLRenderer({antialias:true, logarithmicDepthBuffer:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.localClippingEnabled = true;
vp.appendChild(renderer.domElement);

function onResize(){
  const w = vp.clientWidth, h = vp.clientHeight;
  renderer.setSize(w, h);
  cam.aspect = w/h;
  cam.updateProjectionMatrix();
}
window.addEventListener('resize', onResize);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x060a0f);
scene.fog = new THREE.FogExp2(0x060a0f, 0.007);

const cam = new THREE.PerspectiveCamera(48, 1, 0.05, 2000);
const orb = {theta:0.65, phi:1.05, r:22, tx:0, ty:1.5, tz:0};

function applyOrbit(){
  const sp=Math.sin(orb.phi), cp=Math.cos(orb.phi);
  const st=Math.sin(orb.theta), ct=Math.cos(orb.theta);
  cam.position.set(orb.tx+orb.r*sp*st, orb.ty+orb.r*cp, orb.tz+orb.r*sp*ct);
  cam.lookAt(orb.tx, orb.ty, orb.tz);
}

// Lights
scene.add(new THREE.AmbientLight(0x111a28, 1.0));
const keyL = new THREE.DirectionalLight(0xffffff, 1.3);
keyL.position.set(12,22,10); keyL.castShadow=true;
keyL.shadow.mapSize.set(4096,4096);
['left','right','top','bottom'].forEach((s,i)=>keyL.shadow.camera[s]=[-50,50,50,-50][i]);
keyL.shadow.bias=-0.0002; scene.add(keyL);
scene.add(Object.assign(new THREE.DirectionalLight(0x182850,0.5),{position:{set:()=>{},x:-10,y:5,z:-8}}));
const fl=new THREE.DirectionalLight(0x182850,0.5); fl.position.set(-10,5,-8); scene.add(fl);

// Ground
const gnd = new THREE.Mesh(
  new THREE.PlaneGeometry(400,400),
  new THREE.MeshStandardMaterial({color:0x060a0e,roughness:0.96,metalness:0.04})
);
gnd.rotation.x=-Math.PI/2; gnd.receiveShadow=true; gnd.name='_ground';
scene.add(gnd);

// Grids
const gMaj=new THREE.GridHelper(80,16,0x182838,0x0e1820);
const gMin=new THREE.GridHelper(80,80,0x0c1420,0x0a1018);
gMaj.position.y=0.001; gMin.position.y=0.002;
scene.add(gMaj); scene.add(gMin);

// ═══════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════
let objects=[], selected=null;
const nameCnt={};
// objMeta: Map<mesh, {bbox,dimGrp,normHelper,history,layer,extrudeDepth}>
const objMeta = new Map();
let colorIdx=0;
const COLORS=[0x4a9eff,0xff5555,0x44dd88,0xffcc22,0xaa77ff,0xff8833,0x22ddcc,0xff44aa,0x88ddff,0xff9944];

let transformMode='move', transformSpace='world', aiDetail='brief';
let gizmoGroup=null;

const cadSt = {
  snap:false, snapSz:0.25,
  wire:false, bbox:false, dims:false, normals:false, axes:false,
  measure:false, section:false, sectionY:2,
  clippingPlane: new THREE.Plane(new THREE.Vector3(0,-1,0), 2),
  opMode:null, loftTargets:[], boolTarget:null,
  measurePts:[], measureLine:null,
};
let originAxes=null;

// Material presets
const MAT_PRESETS={
  Steel:    {color:'#8a9aaa',rough:0.30,metal:0.90},
  Aluminium:{color:'#b0c0cc',rough:0.25,metal:0.85},
  Brass:    {color:'#c8a840',rough:0.20,metal:0.80},
  Plastic:  {color:'#3a6aaa',rough:0.70,metal:0.00},
  Concrete: {color:'#707880',rough:0.95,metal:0.00},
  Wood:     {color:'#8a5a30',rough:0.85,metal:0.00},
  Glass:    {color:'#88ccee',rough:0.05,metal:0.10},
};

// ═══════════════════════════════════════════════════
// GEOMETRY FACTORIES
// ═══════════════════════════════════════════════════
function mkGeo(type){
  switch(type){
    case 'box':      return new THREE.BoxGeometry(1.5,1.5,1.5);
    case 'sphere':   return new THREE.SphereGeometry(0.9,48,48);
    case 'cylinder': return new THREE.CylinderGeometry(0.7,0.7,2.0,48);
    case 'cone':     return new THREE.ConeGeometry(0.8,2.0,48);
    case 'torus':    return new THREE.TorusGeometry(0.8,0.25,20,80);
    case 'wedge':    return mkWedgeGeo();
    case 'plane':    return new THREE.PlaneGeometry(2.5,2.5,4,4);
    case 'pipe':     return new THREE.TorusGeometry(0.7,0.1,12,64);
    case 'spring':   return mkSpringGeo(0.6,2.0,10,60);
    default:         return new THREE.BoxGeometry(1.5,1.5,1.5);
  }
}
function mkWedgeGeo(){
  const g=new THREE.BufferGeometry();
  const v=new Float32Array([-0.75,0,-0.75, 0.75,0,-0.75, 0.75,0,0.75, -0.75,0,0.75, -0.75,1.5,-0.75, 0.75,1.5,-0.75]);
  const i=new Uint16Array([0,2,1,0,3,2, 4,1,5,4,0,1, 0,4,3, 1,2,5, 3,5,2,3,4,5]);
  g.setAttribute('position',new THREE.BufferAttribute(v,3));
  g.setIndex(new THREE.BufferAttribute(i,1));
  g.computeVertexNormals(); return g;
}
function mkSpringGeo(r,h,coils,segs){
  const pts=[];
  for(let i=0;i<=segs;i++){
    const t=i/segs, a=t*coils*Math.PI*2;
    pts.push(new THREE.Vector3(Math.cos(a)*r,(t-0.5)*h,Math.sin(a)*r));
  }
  return new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),segs*2,0.06,8,false);
}
function mkMat(color,rough=0.4,metal=0.2,alpha=1.0){
  return new THREE.MeshStandardMaterial({
    color, roughness:rough, metalness:metal,
    transparent:alpha<0.99, opacity:alpha, side:THREE.DoubleSide,
  });
}

// ═══════════════════════════════════════════════════
// ADD PRIMITIVE — always adds, never replaces
// ═══════════════════════════════════════════════════
function addPrim(type){
  const layer = document.getElementById('active-layer').value;
  if(cadSt.layers && cadSt.layers[layer]?.locked){ setMsg('Layer is locked'); return; }

  nameCnt[type]=(nameCnt[type]||0)+1;
  const col=COLORS[colorIdx++%COLORS.length];
  const mat=mkMat(col);
  const geo=mkGeo(type);
  const mesh=new THREE.Mesh(geo,mat);
  mesh.castShadow=true; mesh.receiveShadow=true;

  // Spread new objects so they don't all land on top of each other
  const a=Math.random()*Math.PI*2, r=1.5+Math.random()*2;
  mesh.position.set(Math.cos(a)*r, 0.9, Math.sin(a)*r);

  mesh.userData={type, name:type+'_'+nameCnt[type], layer};
  scene.add(mesh);
  objects.push(mesh);
  objMeta.set(mesh,{bbox:null,dimGrp:null,normHelper:null,history:['created']});

  if(cadSt.bbox) attachBbox(mesh);
  selectObj(mesh);
  updCount();
  setMsg('Added '+mesh.userData.name+' · drag arrows to move · E=extrude');
}

// ═══════════════════════════════════════════════════
// BBOX / DIMS / NORMALS
// ═══════════════════════════════════════════════════
function attachBbox(mesh){
  const m=objMeta.get(mesh); if(!m) return;
  if(m.bbox) scene.remove(m.bbox);
  const h=new THREE.BoxHelper(mesh,0x304860); h.name='_bbox';
  scene.add(h); m.bbox=h;
}
function detachBbox(mesh){
  const m=objMeta.get(mesh); if(!m||!m.bbox) return;
  scene.remove(m.bbox); m.bbox=null;
}
function updateBboxes(){ objMeta.forEach((m)=>{ if(m.bbox) m.bbox.update(); }); }

function attachDims(mesh){
  const m=objMeta.get(mesh); if(!m) return;
  if(m.dimGrp) scene.remove(m.dimGrp);
  const g=new THREE.Group(); g.name='_dim';
  const bb=new THREE.Box3().setFromObject(mesh);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  const ctr=new THREE.Vector3(); bb.getCenter(ctr);
  const lm=new THREE.LineBasicMaterial({color:0x28a0b0,depthTest:false});
  const off=0.4;
  function ln(a,b){ const geo=new THREE.BufferGeometry().setFromPoints([a,b]);
    const l=new THREE.Line(geo,lm); l.renderOrder=5; g.add(l); }
  const xA=new THREE.Vector3(bb.min.x,bb.min.y-off,ctr.z);
  const xB=new THREE.Vector3(bb.max.x,bb.min.y-off,ctr.z);
  ln(xA,xB); ln(new THREE.Vector3(bb.min.x,bb.min.y,ctr.z),xA); ln(new THREE.Vector3(bb.max.x,bb.min.y,ctr.z),xB);
  const yA=new THREE.Vector3(bb.max.x+off,bb.min.y,ctr.z);
  const yB=new THREE.Vector3(bb.max.x+off,bb.max.y,ctr.z);
  ln(yA,yB); ln(new THREE.Vector3(bb.max.x,bb.min.y,ctr.z),yA); ln(new THREE.Vector3(bb.max.x,bb.max.y,ctr.z),yB);
  scene.add(g); m.dimGrp=g;
}
function detachDims(mesh){
  const m=objMeta.get(mesh); if(!m||!m.dimGrp) return;
  scene.remove(m.dimGrp); m.dimGrp=null;
}
function attachNormals(mesh){
  const m=objMeta.get(mesh); if(!m) return;
  try{
    if(m.normHelper) scene.remove(m.normHelper);
    m.normHelper=new THREE.VertexNormalsHelper(mesh,0.2,0x00ee88);
    scene.add(m.normHelper);
  }catch(e){}
}
function detachNormals(mesh){
  const m=objMeta.get(mesh); if(!m||!m.normHelper) return;
  scene.remove(m.normHelper); m.normHelper=null;
}

// ═══════════════════════════════════════════════════
// REMOVE OBJECT
// ═══════════════════════════════════════════════════
function removeObj(mesh){
  const m=objMeta.get(mesh);
  if(m?.bbox) scene.remove(m.bbox);
  if(m?.dimGrp) scene.remove(m.dimGrp);
  if(m?.normHelper) scene.remove(m.normHelper);
  objMeta.delete(mesh);
  scene.remove(mesh);
  objects=objects.filter(o=>o!==mesh);
  if(selected===mesh){ selected=null; buildGizmo(); updatePropsPanel(null); }
}

// ═══════════════════════════════════════════════════
// CAD OPERATIONS
// ═══════════════════════════════════════════════════

// EXTRUDE — builds a NEW extruded box on top of the selected object.
// The original is preserved. The new mesh is added to the scene.
function cadExtrude(){
  if(!selected){ setMsg('Select an object first'); return; }
  const depth = parseFloat(document.getElementById('ext-depth').value);
  const src = selected;
  const bb = new THREE.Box3().setFromObject(src);
  const sz = new THREE.Vector3(); bb.getSize(sz);
  const ctr = new THREE.Vector3(); bb.getCenter(ctr);

  // New extruded mesh: same footprint (X/Z), new height
  nameCnt['extrude']=(nameCnt['extrude']||0)+1;
  const extGeo = new THREE.BoxGeometry(sz.x, depth, sz.z);
  const extMat = src.material.clone();
  extMat.color = src.material.color.clone();
  const extMesh = new THREE.Mesh(extGeo, extMat);
  extMesh.castShadow=true; extMesh.receiveShadow=true;

  // Place it on top of the source object
  extMesh.position.set(ctr.x, bb.max.y + depth/2, ctr.z);
  extMesh.rotation.copy(src.rotation);

  const nm = src.userData.name+'_ext'+nameCnt['extrude'];
  extMesh.userData = {type:'extrude', name:nm, layer:src.userData.layer||'Layer 0'};
  scene.add(extMesh);
  objects.push(extMesh);
  objMeta.set(extMesh,{bbox:null,dimGrp:null,normHelper:null,history:['extruded_from:'+src.userData.name+':depth='+depth.toFixed(2)]});
  if(cadSt.bbox) attachBbox(extMesh);
  selectObj(extMesh);
  updCount();
  setMsg('Extruded '+src.userData.name+' → '+nm+' (h='+depth.toFixed(2)+') · original preserved');
}

// REVOLVE — adds a revolved cylinder version on top of selected, keeps original
function cadRevolve(){
  if(!selected){ setMsg('Select an object first'); return; }
  const src=selected;
  const bb=new THREE.Box3().setFromObject(src);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  const ctr=new THREE.Vector3(); bb.getCenter(ctr);
  const radius=Math.max(sz.x,sz.z)*0.55;
  nameCnt['rev']=(nameCnt['rev']||0)+1;
  const m=new THREE.Mesh(new THREE.CylinderGeometry(radius,radius,sz.y,64), src.material.clone());
  m.castShadow=true; m.receiveShadow=true;
  m.position.copy(src.position);
  const nm=src.userData.name+'_rev'+nameCnt['rev'];
  m.userData={type:'revolve',name:nm,layer:src.userData.layer||'Layer 0'};
  scene.add(m); objects.push(m);
  objMeta.set(m,{bbox:null,dimGrp:null,normHelper:null,history:['revolved_from:'+src.userData.name]});
  if(cadSt.bbox) attachBbox(m);
  selectObj(m); updCount();
  setMsg('Revolved '+src.userData.name+' → '+nm+' (original preserved)');
}

// SHELL — makes selected semi-transparent, adds inner shell mesh
function cadShell(){
  if(!selected){ setMsg('Select an object first'); return; }
  const thickness=parseFloat(document.getElementById('shell-t').value);
  const src=selected;
  const bb=new THREE.Box3().setFromObject(src);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  const iw=Math.max(0.01,sz.x-thickness*2);
  const ih=Math.max(0.01,sz.y-thickness*2);
  const id=Math.max(0.01,sz.z-thickness*2);
  const innerMat=src.material.clone();
  innerMat.side=THREE.BackSide;
  const inner=new THREE.Mesh(new THREE.BoxGeometry(iw,ih,id), innerMat);
  inner.position.copy(src.position);
  inner.rotation.copy(src.rotation);
  nameCnt['shell']=(nameCnt['shell']||0)+1;
  const nm=src.userData.name+'_shell'+nameCnt['shell'];
  inner.userData={type:'shell_inner',name:nm,layer:src.userData.layer||'Layer 0'};
  scene.add(inner); objects.push(inner);
  objMeta.set(inner,{bbox:null,dimGrp:null,normHelper:null,history:['shell_of:'+src.userData.name]});
  src.material.transparent=true; src.material.opacity=0.35; src.material.needsUpdate=true;
  pushHist(src,'shelled:t='+thickness.toFixed(3));
  selectObj(inner); updCount();
  setMsg('Shelled '+src.userData.name+' → wall '+thickness.toFixed(3));
}

// MIRROR — adds mirrored copy
function cadMirror(axis){
  if(!selected){ setMsg('Select an object first'); return; }
  const src=selected;
  const cp=src.clone(); cp.material=src.material.clone();
  if(axis==='X') cp.scale.x*=-1;
  else if(axis==='Y') cp.scale.y*=-1;
  else cp.scale.z*=-1;
  const t=src.userData.type; nameCnt[t]=(nameCnt[t]||0)+1;
  const nm=src.userData.name+'_mir'+nameCnt[t];
  cp.userData={...src.userData,name:nm};
  scene.add(cp); objects.push(cp);
  objMeta.set(cp,{bbox:null,dimGrp:null,normHelper:null,history:['mirror_'+axis+'_of:'+src.userData.name]});
  if(cadSt.bbox) attachBbox(cp);
  selectObj(cp); updCount();
  setMsg('Mirrored → '+nm);
}

// FILLET — visual approximation: adds a torus ring around the base of selected
function cadFillet(){
  if(!selected){ setMsg('Select an object first'); return; }
  const src=selected;
  const bb=new THREE.Box3().setFromObject(src);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  const r=Math.min(sz.x,sz.z)*0.52;
  const fMat=src.material.clone();
  const fMesh=new THREE.Mesh(new THREE.TorusGeometry(r,0.08,12,48),fMat);
  fMesh.position.set(src.position.x, bb.min.y+0.06, src.position.z);
  fMesh.rotation.x=Math.PI/2;
  nameCnt['fillet']=(nameCnt['fillet']||0)+1;
  const nm=src.userData.name+'_fillet'+nameCnt['fillet'];
  fMesh.userData={type:'fillet',name:nm,layer:src.userData.layer||'Layer 0'};
  scene.add(fMesh); objects.push(fMesh);
  objMeta.set(fMesh,{bbox:null,dimGrp:null,normHelper:null,history:['fillet_of:'+src.userData.name]});
  if(cadSt.bbox) attachBbox(fMesh);
  selectObj(fMesh); updCount();
  setMsg('Fillet ring added at base of '+src.userData.name);
}

// ARRAY — creates N copies; orignal stays
function cadArray(){
  if(!selected){ setMsg('Select an object first'); return; }
  const count=parseInt(document.getElementById('arr-n').value)||3;
  const spacing=parseFloat(document.getElementById('arr-sp').value)||2.5;
  const axis=document.getElementById('arr-ax').value;
  const type=document.getElementById('arr-ty').value;
  const src=selected;
  for(let i=1;i<count;i++){
    const cp=src.clone(); cp.material=src.material.clone();
    const t=src.userData.type; nameCnt[t]=(nameCnt[t]||0)+1;
    cp.userData={...src.userData,name:t+'_arr'+nameCnt[t]};
    cp.position.copy(src.position);
    if(type==='Linear'){
      if(axis==='X') cp.position.x+=spacing*i;
      else if(axis==='Y') cp.position.y+=spacing*i;
      else cp.position.z+=spacing*i;
    } else {
      const a=(Math.PI*2/count)*i;
      cp.position.x=src.position.x+Math.cos(a)*spacing;
      cp.position.z=src.position.z+Math.sin(a)*spacing;
      cp.rotation.y=a;
    }
    scene.add(cp); objects.push(cp);
    objMeta.set(cp,{bbox:null,dimGrp:null,normHelper:null,history:['array_copy:'+i+':of:'+src.userData.name]});
    if(cadSt.bbox) attachBbox(cp);
  }
  pushHist(src,'arrayed:'+type+':'+count);
  updCount(); setMsg('Array: '+count+' copies of '+src.userData.name+' ('+type+'/'+axis+')');
}

// LOFT — two-click: click Loft btn then click two objects
function startLoft(){
  cadSt.opMode='loft'; cadSt.loftTargets=[];
  setOpOverlay('LOFT — click 2 profile objects');
  document.getElementById('sb-mode').textContent='LOFT';
  document.getElementById('sb-mode').className='sc on';
  setMsg('LOFT: click first profile object');
}
function finishLoft(){
  const [a,b]=cadSt.loftTargets;
  const bbA=new THREE.Box3().setFromObject(a), cA=new THREE.Vector3(); bbA.getCenter(cA);
  const bbB=new THREE.Box3().setFromObject(b), cB=new THREE.Vector3(); bbB.getCenter(cB);
  const szA=new THREE.Vector3(); bbA.getSize(szA);
  const szB=new THREE.Vector3(); bbB.getSize(szB);
  const rA=Math.max(szA.x,szA.z)*0.45, rB=Math.max(szB.x,szB.z)*0.45;
  const curve=new THREE.CatmullRomCurve3([
    cA.clone(),
    new THREE.Vector3((cA.x+cB.x)/2,(cA.y+cB.y)/2+Math.abs(cB.y-cA.y)*0.4+0.5,(cA.z+cB.z)/2),
    cB.clone()
  ]);
  const geo=new THREE.TubeGeometry(curve,40,(rA+rB)/2,16,false);
  const mat=mkMat(COLORS[colorIdx++%COLORS.length]);
  const lm=new THREE.Mesh(geo,mat);
  lm.castShadow=true; lm.receiveShadow=true;
  nameCnt['loft']=(nameCnt['loft']||0)+1;
  const nm='loft_'+nameCnt['loft'];
  lm.userData={type:'loft',name:nm,layer:'Layer 0'};
  scene.add(lm); objects.push(lm);
  objMeta.set(lm,{bbox:null,dimGrp:null,normHelper:null,history:['loft:'+a.userData.name+'→'+b.userData.name]});
  a.material.emissive?.setHex(0x000000);
  b.material.emissive?.setHex(0x000000);
  cadSt.opMode=null; cadSt.loftTargets=[];
  setOpOverlay(null);
  document.getElementById('sb-mode').textContent='NAVIGATE';
  document.getElementById('sb-mode').className='sc';
  selectObj(lm); updCount();
  setMsg('Loft created: '+nm);
}

// BOOLEAN
function startBoolean(op){
  if(!selected){ setMsg('Select the first object for boolean '+op); return; }
  cadSt.opMode='bool-'+op; cadSt.boolTarget=selected;
  selected.material.emissive?.setHex(0x183060);
  setOpOverlay('BOOLEAN '+op.toUpperCase()+' — click second object');
  document.getElementById('sb-mode').textContent='BOOL:'+op.toUpperCase();
  document.getElementById('sb-mode').className='sc warn';
  setMsg('BOOLEAN '+op+': now click the second object');
}
function finishBoolean(op, objA, objB){
  if(op==='union'){
    const gA=objA.geometry.clone(); gA.applyMatrix4(objA.matrixWorld);
    const gB=objB.geometry.clone(); gB.applyMatrix4(objB.matrixWorld);
    const merged=mergeGeos(gA,gB);
    const mat=mkMat(objA.material.color.getHex(),objA.material.roughness,objA.material.metalness);
    const rm=new THREE.Mesh(merged,mat);
    rm.castShadow=true; rm.receiveShadow=true;
    nameCnt['union']=(nameCnt['union']||0)+1;
    rm.userData={type:'union',name:'union_'+nameCnt['union'],layer:'Layer 0'};
    scene.add(rm); objects.push(rm);
    objMeta.set(rm,{bbox:null,dimGrp:null,normHelper:null,history:['union:'+objA.userData.name+'+'+objB.userData.name]});
    removeObj(objA); removeObj(objB);
    selectObj(rm);
    setMsg('Boolean union → union_'+nameCnt['union']);
  } else {
    // Subtract: clip A using B's bounding box plane
    const bbB=new THREE.Box3().setFromObject(objB);
    objA.material.clippingPlanes=[new THREE.Plane(new THREE.Vector3(-1,0,0),bbB.max.x)];
    pushHist(objA,'subtract:'+objB.userData.name);
    removeObj(objB);
    setMsg('Subtracted '+objB.userData.name+' from '+objA.userData.name);
  }
  cadSt.opMode=null; cadSt.boolTarget=null;
  setOpOverlay(null);
  document.getElementById('sb-mode').textContent='NAVIGATE';
  document.getElementById('sb-mode').className='sc';
  updCount();
}
function mergeGeos(gA,gB){
  const posA=gA.getAttribute('position'), posB=gB.getAttribute('position');
  const arr=new Float32Array(posA.count*3+posB.count*3);
  arr.set(posA.array,0); arr.set(posB.array,posA.count*3);
  const out=new THREE.BufferGeometry();
  out.setAttribute('position',new THREE.BufferAttribute(arr,3));
  out.computeVertexNormals(); return out;
}

function pushHist(mesh,op){
  const m=objMeta.get(mesh); if(!m) return;
  if(!m.history) m.history=[];
  m.history.push(op); updateHUD();
}
function setOpOverlay(msg){
  const el=document.getElementById('op-overlay');
  if(!msg){el.style.display='none';return;}
  el.textContent=msg; el.style.display='block';
}

// ═══════════════════════════════════════════════════
// GIZMO
// ═══════════════════════════════════════════════════
const AX={x:0xff2222,y:0x22ee22,z:0x2244ff};
function buildGizmo(){
  if(gizmoGroup){scene.remove(gizmoGroup);gizmoGroup=null;}
  if(!selected) return;
  gizmoGroup=new THREE.Group(); gizmoGroup.name='_gizmo';
  if(transformMode==='move') buildMoveGiz();
  else if(transformMode==='rotate') buildRotGiz();
  else buildScaleGiz();
  scene.add(gizmoGroup); syncGizmo();
}
function buildMoveGiz(){
  ['x','y','z'].forEach(ax=>{
    const s=new THREE.Mesh(new THREE.CylinderGeometry(0.032,0.032,1.9,8),
      new THREE.MeshBasicMaterial({color:AX[ax],depthTest:false}));
    const t=new THREE.Mesh(new THREE.ConeGeometry(0.095,0.28,8),
      new THREE.MeshBasicMaterial({color:AX[ax],depthTest:false}));
    t.position.y=1.1;
    const a=new THREE.Group(); a.add(s,t); a.userData.axis=ax;
    if(ax==='x'){a.rotation.z=-Math.PI/2;a.position.x=1.0;}
    else if(ax==='y') a.position.y=1.0;
    else{a.rotation.x=Math.PI/2;a.position.z=1.0;}
    gizmoGroup.add(a);
  });
  [['xz',0xeeee00,[-Math.PI/2,0,0],[0.5,0,0.5]],
   ['xy',0x00eeee,[0,0,0],[0.5,0.5,0]],
   ['yz',0xee00ee,[0,Math.PI/2,0],[0,0.5,0.5]]].forEach(([ax,c,rot,pos])=>{
    const sq=new THREE.Mesh(new THREE.PlaneGeometry(0.4,0.4),
      new THREE.MeshBasicMaterial({color:c,transparent:true,opacity:0.2,side:THREE.DoubleSide,depthTest:false}));
    sq.userData.axis=ax; sq.rotation.set(...rot); sq.position.set(...pos);
    gizmoGroup.add(sq);
  });
}
function buildRotGiz(){
  [['x',0xff2222,[0,0,Math.PI/2]],['y',0x22ee22,[0,0,0]],['z',0x2244ff,[Math.PI/2,0,0]]].forEach(([ax,c,r])=>{
    const ring=new THREE.Mesh(new THREE.TorusGeometry(1.1,0.032,8,64),
      new THREE.MeshBasicMaterial({color:c,depthTest:false}));
    ring.userData.axis=ax; ring.rotation.set(...r); gizmoGroup.add(ring);
  });
}
function buildScaleGiz(){
  ['x','y','z'].forEach(ax=>{
    const s=new THREE.Mesh(new THREE.CylinderGeometry(0.032,0.032,1.9,8),
      new THREE.MeshBasicMaterial({color:AX[ax],depthTest:false}));
    const cb=new THREE.Mesh(new THREE.BoxGeometry(0.18,0.18,0.18),
      new THREE.MeshBasicMaterial({color:AX[ax],depthTest:false}));
    cb.position.y=1.1;
    const a=new THREE.Group(); a.add(s,cb); a.userData.axis=ax;
    if(ax==='x'){a.rotation.z=-Math.PI/2;a.position.x=1.0;}
    else if(ax==='y') a.position.y=1.0;
    else{a.rotation.x=Math.PI/2;a.position.z=1.0;}
    gizmoGroup.add(a);
  });
  const uni=new THREE.Mesh(new THREE.SphereGeometry(0.12,8,8),
    new THREE.MeshBasicMaterial({color:0xffffff,depthTest:false}));
  uni.userData.axis='xyz'; gizmoGroup.add(uni);
}
function syncGizmo(){
  if(!selected||!gizmoGroup) return;
  gizmoGroup.position.copy(selected.position);
  const bb=new THREE.Box3().setFromObject(selected);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  gizmoGroup.scale.setScalar(Math.max(sz.x,sz.y,sz.z)*0.38+0.55);
  if(transformSpace==='local') gizmoGroup.rotation.copy(selected.rotation);
  else gizmoGroup.rotation.set(0,0,0);
}

// ═══════════════════════════════════════════════════
// SELECT
// ═══════════════════════════════════════════════════
function selectObj(obj){
  if(selected&&selected!==obj){
    selected.material.emissive?.setHex(0x000000);
    if(!cadSt.dims) detachDims(selected);
    if(!cadSt.normals) detachNormals(selected);
  }
  selected=obj;
  if(selected){
    selected.material.emissive?.setHex(0x0c2438);
    buildGizmo(); syncGizmo();
    if(cadSt.dims) attachDims(selected);
    if(cadSt.normals) attachNormals(selected);
    updatePropsPanel(selected);
    updateHUD();
    // Sync sidebar inputs
    const p=selected.position, r=selected.rotation, s=selected.scale;
    document.getElementById('in-px').value=p.x.toFixed(3);
    document.getElementById('in-py').value=p.y.toFixed(3);
    document.getElementById('in-pz').value=p.z.toFixed(3);
    document.getElementById('in-rx').value=(r.x*180/Math.PI).toFixed(1);
    document.getElementById('in-ry').value=(r.y*180/Math.PI).toFixed(1);
    document.getElementById('in-rz').value=(r.z*180/Math.PI).toFixed(1);
    document.getElementById('in-sx').value=s.x.toFixed(3);
    document.getElementById('in-sy').value=s.y.toFixed(3);
    document.getElementById('in-sz').value=s.z.toFixed(3);
    setMsg('['+selected.userData.name+'] · E=extrude · X=AI analyze · F=frame · D=dup');
  } else {
    if(gizmoGroup){scene.remove(gizmoGroup);gizmoGroup=null;}
    updatePropsPanel(null); updateHUD();
  }
}

// ═══════════════════════════════════════════════════
// UI UPDATES
// ═══════════════════════════════════════════════════
function updatePropsPanel(mesh){
  const panel=document.getElementById('props');
  if(!mesh){panel.style.display='none';return;}
  panel.style.display='block';
  document.getElementById('props-type').textContent=mesh.userData.type?.toUpperCase()||'';
  const bb=new THREE.Box3().setFromObject(mesh);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  const p=mesh.position, r=mesh.rotation, s=mesh.scale;
  const col='#'+mesh.material.color.getHexString();
  const m=objMeta.get(mesh);
  const hist=(m?.history||[]).slice(-3).join(' → ')||'--';
  document.getElementById('props-body').innerHTML=`
    <div class="ph">Transform</div>
    <div class="pr"><span class="pl">X</span><span class="pv">${p.x.toFixed(3)}</span></div>
    <div class="pr"><span class="pl">Y</span><span class="pv">${p.y.toFixed(3)}</span></div>
    <div class="pr"><span class="pl">Z</span><span class="pv">${p.z.toFixed(3)}</span></div>
    <div class="pr"><span class="pl">Rx°</span><span class="pv">${(r.x*57.3).toFixed(1)}</span></div>
    <div class="pr"><span class="pl">Ry°</span><span class="pv">${(r.y*57.3).toFixed(1)}</span></div>
    <div class="pr"><span class="pl">Rz°</span><span class="pv">${(r.z*57.3).toFixed(1)}</span></div>
    <div class="ph">Bounding Box</div>
    <div class="pr"><span class="pl">W</span><span class="pv">${sz.x.toFixed(3)}</span></div>
    <div class="pr"><span class="pl">H</span><span class="pv">${sz.y.toFixed(3)}</span></div>
    <div class="pr"><span class="pl">D</span><span class="pv">${sz.z.toFixed(3)}</span></div>
    <div class="pr"><span class="pl">Vol≈</span><span class="pv">${(sz.x*sz.y*sz.z).toFixed(3)} u³</span></div>
    <div class="ph">Material</div>
    <div class="pr"><span class="pl">Color</span><span class="pv">${col}</span></div>
    <div class="pr"><span class="pl">Rough</span><span class="pv">${mesh.material.roughness?.toFixed(3)||'--'}</span></div>
    <div class="pr"><span class="pl">Metal</span><span class="pv">${mesh.material.metalness?.toFixed(3)||'--'}</span></div>
    <div class="ph">History</div>
    <div class="pr"><span class="pv" style="font-size:9px;color:#1a4060;word-break:break-all;">${hist}</span></div>
    <div class="ph">Layer</div>
    <div class="pr"><span class="pv">${mesh.userData.layer||'Layer 0'}</span></div>
  `;
}
function updateHUD(){
  const cp=cam.position;
  document.getElementById('hud-cam').textContent=cp.x.toFixed(1)+', '+cp.y.toFixed(1)+', '+cp.z.toFixed(1);
  document.getElementById('hud-cnt').textContent;
  if(selected){
    const sp=selected.position, sr=selected.rotation;
    const bb=new THREE.Box3().setFromObject(selected);
    const sz=new THREE.Vector3(); bb.getSize(sz);
    const m=objMeta.get(selected);
    document.getElementById('hud-sel').style.display='block';
    document.getElementById('hud-name').textContent=selected.userData.name;
    document.getElementById('hud-pos').textContent=sp.x.toFixed(2)+', '+sp.y.toFixed(2)+', '+sp.z.toFixed(2);
    document.getElementById('hud-sz').textContent=sz.x.toFixed(2)+' × '+sz.y.toFixed(2)+' × '+sz.z.toFixed(2);
    document.getElementById('hud-ops').textContent=(m?.history||[]).slice(-2).join(' → ')||'--';
  } else {
    document.getElementById('hud-sel').style.display='none';
  }
}
function updCount(){
  document.getElementById('sb-objs').textContent='OBJS:'+objects.length;
}

// ═══════════════════════════════════════════════════
// TRANSFORM FROM SIDEBAR INPUTS
// ═══════════════════════════════════════════════════
function applyPos(){
  if(!selected) return;
  selected.position.set(
    parseFloat(document.getElementById('in-px').value)||0,
    parseFloat(document.getElementById('in-py').value)||0,
    parseFloat(document.getElementById('in-pz').value)||0
  );
  syncGizmo(); updateBboxes(); updatePropsPanel(selected);
}
function applyRot(){
  if(!selected) return;
  selected.rotation.set(
    (parseFloat(document.getElementById('in-rx').value)||0)*Math.PI/180,
    (parseFloat(document.getElementById('in-ry').value)||0)*Math.PI/180,
    (parseFloat(document.getElementById('in-rz').value)||0)*Math.PI/180
  );
  syncGizmo(); updateBboxes(); updatePropsPanel(selected);
}
function applyScale(){
  if(!selected) return;
  selected.scale.set(
    Math.max(0.001,parseFloat(document.getElementById('in-sx').value)||1),
    Math.max(0.001,parseFloat(document.getElementById('in-sy').value)||1),
    Math.max(0.001,parseFloat(document.getElementById('in-sz').value)||1)
  );
  syncGizmo(); updateBboxes(); updatePropsPanel(selected);
}

// ═══════════════════════════════════════════════════
// MATERIAL
// ═══════════════════════════════════════════════════
function applyMatPreset(name){
  if(!selected||name==='Custom') return;
  const p=MAT_PRESETS[name]; if(!p) return;
  selected.material.color.set(p.color);
  selected.material.roughness=p.rough;
  selected.material.metalness=p.metal;
  selected.material.needsUpdate=true;
  document.getElementById('mat-color').value=p.color;
  document.getElementById('mat-rough').value=p.rough;
  document.getElementById('mat-metal').value=p.metal;
  pushHist(selected,'mat:'+name);
  updatePropsPanel(selected);
  setMsg('Material: '+name+' applied to '+selected.userData.name);
}
function applyMatCustom(){
  if(!selected) return;
  selected.material.color.set(document.getElementById('mat-color').value);
  selected.material.roughness=parseFloat(document.getElementById('mat-rough').value);
  selected.material.metalness=parseFloat(document.getElementById('mat-metal').value);
  const alpha=parseFloat(document.getElementById('mat-alpha').value);
  selected.material.transparent=alpha<0.99;
  selected.material.opacity=alpha;
  selected.material.needsUpdate=true;
  updatePropsPanel(selected);
}

// ═══════════════════════════════════════════════════
// VIEW TOGGLES
// ═══════════════════════════════════════════════════
function setTransformMode(m){
  transformMode=m;
  ['move','rotate','scale'].forEach(x=>{
    const btn=document.getElementById('btn-'+x);
    if(btn) btn.className='third'+(x===m?' active':'');
  });
  buildGizmo();
  document.getElementById('sb-mode').textContent=m.toUpperCase()+' · '+transformSpace.toUpperCase();
}
function setSpace(s){
  transformSpace=s;
  document.getElementById('btn-world').className='half'+(s==='world'?' active':'');
  document.getElementById('btn-local').className='half'+(s==='local'?' active':'');
  syncGizmo();
}
function setDetail(d){
  aiDetail=d;
  document.getElementById('btn-brief').className='half'+(d==='brief'?' active':'');
  document.getElementById('btn-detailed').className='half'+(d==='detailed'?' active':'');
}

function toggleWire(){
  cadSt.wire=!cadSt.wire;
  objects.forEach(o=>{if(o.material)o.material.wireframe=cadSt.wire;});
  document.getElementById('btn-wire').className='half'+(cadSt.wire?' active':'');
  document.getElementById('sb-wire').textContent='WIRE:'+(cadSt.wire?'ON':'OFF');
  setMsg('Wireframe '+(cadSt.wire?'ON':'OFF'));
}
function toggleBbox(){
  cadSt.bbox=!cadSt.bbox;
  objects.forEach(o=>{if(cadSt.bbox)attachBbox(o);else detachBbox(o);});
  document.getElementById('btn-bbox').className='half'+(cadSt.bbox?' active':'');
  setMsg('Bbox '+(cadSt.bbox?'ON':'OFF'));
}
function toggleDims(){
  cadSt.dims=!cadSt.dims;
  if(!cadSt.dims) objMeta.forEach((_,m)=>detachDims(m));
  else if(selected) attachDims(selected);
  document.getElementById('btn-dims').className='half'+(cadSt.dims?' active':'');
  setMsg('Dimensions '+(cadSt.dims?'ON':'OFF'));
}
function toggleAxes(){
  cadSt.axes=!cadSt.axes;
  if(originAxes){scene.remove(originAxes);originAxes=null;}
  if(cadSt.axes){
    originAxes=new THREE.Group();
    [[1,0,0,0xff2222],[0,1,0,0x22ff22],[0,0,1,0x2244ff]].forEach(([x,y,z,c])=>{
      const pts=[new THREE.Vector3(0,0,0),new THREE.Vector3(x,y,z).multiplyScalar(8)];
      const l=new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({color:c,depthTest:false}));
      l.renderOrder=10; originAxes.add(l);
    });
    scene.add(originAxes);
  }
  document.getElementById('btn-axes').className='half'+(cadSt.axes?' active':'');
  setMsg('Axes '+(cadSt.axes?'ON':'OFF'));
}
function toggleMeasure(){
  cadSt.measure=!cadSt.measure;
  cadSt.measurePts=[];
  if(cadSt.measureLine){scene.remove(cadSt.measureLine);cadSt.measureLine=null;}
  document.getElementById('measure-panel').style.display=cadSt.measure?'block':'none';
  document.getElementById('mp-txt').textContent='Click first point';
  document.getElementById('btn-measure').className='half'+(cadSt.measure?' active':'');
  document.getElementById('sb-mode').textContent=cadSt.measure?'MEASURE':'NAVIGATE';
  document.getElementById('sb-mode').className='sc'+(cadSt.measure?' on':'');
  setMsg('Measure '+(cadSt.measure?'ON — click two points':'OFF'));
}
function toggleSection(){
  cadSt.section=!cadSt.section;
  document.getElementById('section-ctrl').style.display=cadSt.section?'flex':'none';
  if(cadSt.section){
    objects.forEach(o=>{o.material.clippingPlanes=[cadSt.clippingPlane];o.material.clipShadows=true;});
    renderer.localClippingEnabled=true;
  } else {
    objects.forEach(o=>{o.material.clippingPlanes=[];});
    renderer.localClippingEnabled=false;
  }
  document.getElementById('btn-section').className='half'+(cadSt.section?' active':'');
  setMsg('Section '+(cadSt.section?'ON':'OFF'));
}
function moveSectionPlane(y){
  cadSt.sectionY=y; cadSt.clippingPlane.constant=y;
  setMsg('Section Y='+y.toFixed(2));
}
function setView(v){
  if(v==='Top'){orb.phi=0.01;orb.theta=0;}
  else if(v==='Front'){orb.phi=Math.PI/2;orb.theta=0;}
  else if(v==='Right'){orb.phi=Math.PI/2;orb.theta=Math.PI/2;}
  else if(v==='Isometric'){orb.phi=0.9553;orb.theta=0.7854;}
  else{orb.phi=1.05;orb.theta=0.65;}
  setMsg('View: '+v);
}
function layerVis(){
  const n=document.getElementById('active-layer').value;
  if(!cadSt.layerState) cadSt.layerState={};
  if(!cadSt.layerState[n]) cadSt.layerState[n]={vis:true,locked:false};
  cadSt.layerState[n].vis=!cadSt.layerState[n].vis;
  objects.forEach(o=>{if(o.userData.layer===n)o.visible=cadSt.layerState[n].vis;});
  setMsg('Layer ['+n+'] '+(cadSt.layerState[n].vis?'visible':'hidden'));
}
function layerLock(){
  const n=document.getElementById('active-layer').value;
  if(!cadSt.layerState) cadSt.layerState={};
  if(!cadSt.layerState[n]) cadSt.layerState[n]={vis:true,locked:false};
  cadSt.layerState[n].locked=!cadSt.layerState[n].locked;
  setMsg('Layer ['+n+'] '+(cadSt.layerState[n].locked?'LOCKED':'unlocked'));
}

// ═══════════════════════════════════════════════════
// SCENE OPS
// ═══════════════════════════════════════════════════
function duplicate(){
  if(!selected){setMsg('Nothing selected');return;}
  const src=selected;
  const cp=src.clone(); cp.material=src.material.clone();
  cp.position.x+=2;
  const t=src.userData.type; nameCnt[t]=(nameCnt[t]||0)+1;
  cp.userData={...src.userData,name:t+'_'+nameCnt[t]};
  scene.add(cp); objects.push(cp);
  objMeta.set(cp,{bbox:null,dimGrp:null,normHelper:null,history:['dup_of:'+src.userData.name]});
  if(cadSt.bbox) attachBbox(cp);
  selectObj(cp); updCount();
  setMsg('Duplicated → '+cp.userData.name);
}
function deleteSel(){
  if(!selected){setMsg('Nothing selected');return;}
  removeObj(selected); selected=null;
  if(gizmoGroup){scene.remove(gizmoGroup);gizmoGroup=null;}
  setMsg('Deleted'); updCount();
}
function clearScene(){
  if(!confirm('Clear all objects?')) return;
  [...objects].forEach(o=>removeObj(o));
  objects=[]; colorIdx=0;
  Object.keys(nameCnt).forEach(k=>delete nameCnt[k]);
  selected=null;
  document.getElementById('ai-gen-panel').style.display='none';
  document.getElementById('ai-analyze-panel').style.display='none';
  setMsg('Scene cleared'); updCount();
}
function frameSelected(){
  if(!selected){orb.r=24;orb.tx=0;orb.ty=2;orb.tz=0;setMsg('Framed scene');return;}
  const bb=new THREE.Box3().setFromObject(selected);
  const ctr=new THREE.Vector3(); bb.getCenter(ctr);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  orb.tx=ctr.x; orb.ty=ctr.y; orb.tz=ctr.z;
  orb.r=Math.max(sz.x,sz.y,sz.z)*3+5;
  setMsg('Framed: '+selected.userData.name);
}

// ═══════════════════════════════════════════════════
// MEASURE
// ═══════════════════════════════════════════════════
function doMeasure(ev){
  const hits=getHits(ev,[...objects,gnd]);
  if(!hits.length) return;
  let pt=hits[0].point.clone();
  if(cadSt.snap){
    pt.x=Math.round(pt.x/cadSt.snapSz)*cadSt.snapSz;
    pt.z=Math.round(pt.z/cadSt.snapSz)*cadSt.snapSz;
  }
  cadSt.measurePts.push(pt);
  if(cadSt.measurePts.length===1){
    document.getElementById('mp-txt').textContent=
      'P1=('+pt.x.toFixed(2)+', '+pt.y.toFixed(2)+', '+pt.z.toFixed(2)+') — click 2nd';
  }
  if(cadSt.measurePts.length===2){
    const [p1,p2]=cadSt.measurePts;
    const dist=p1.distanceTo(p2);
    const dx=Math.abs(p2.x-p1.x),dy=Math.abs(p2.y-p1.y),dz=Math.abs(p2.z-p1.z);
    if(cadSt.measureLine) scene.remove(cadSt.measureLine);
    const geo=new THREE.BufferGeometry().setFromPoints([p1,p2]);
    cadSt.measureLine=new THREE.Line(geo,
      new THREE.LineDashedMaterial({color:0x28d0f0,dashSize:0.13,gapSize:0.06,depthTest:false}));
    cadSt.measureLine.computeLineDistances(); scene.add(cadSt.measureLine);
    document.getElementById('mp-txt').textContent='Δ='+dist.toFixed(4)+' | X='+dx.toFixed(3)+' Y='+dy.toFixed(3)+' Z='+dz.toFixed(3);
    document.getElementById('sb-dist').textContent='DIST:'+dist.toFixed(4)+'u';
    cadSt.measurePts=[];
  }
}

// ═══════════════════════════════════════════════════
// AI GENERATOR
// ═══════════════════════════════════════════════════
async function runGenerator(){
  const prompt=document.getElementById('ai-prompt').value.trim();
  if(!prompt){setMsg('Enter a design description first');return;}
  const apiKey=CFG.apiKey;
  const model=document.getElementById('ai-model').value;
  if(!apiKey){setMsg('No API key — add OPENROUTER_API_KEY to .streamlit/secrets.toml');return;}

  const panel=document.getElementById('ai-gen-panel');
  const body=document.getElementById('ai-gen-body');
  panel.style.display='flex';
  body.innerHTML='<div class="ldg"><span>Generating design</span><span class="dot">■</span><span class="dot">■</span><span class="dot">■</span></div>';
  setMsg('Asking Claude to generate design: "'+prompt+'"…');

  const sys=`You are an expert CAD automation engine. Respond ONLY with a valid JSON object — no markdown, no explanation, no preamble.
Schema:
{
  "name": "short design name",
  "description": "1 sentence summary",
  "objects": [
    {
      "name": "unique string",
      "type": "box|sphere|cylinder|cone|torus|wedge|plane|pipe|spring",
      "position": [x, y, z],
      "rotation": [rx_deg, ry_deg, rz_deg],
      "scale": [sx, sy, sz],
      "color": "#rrggbb",
      "roughness": 0.0-1.0,
      "metalness": 0.0-1.0,
      "note": "brief engineering note"
    }
  ],
  "notes": "overall design notes"
}
Rules:
- Y is UP. Ground is Y=0. Stack parts by increasing Y.
- Use realistic engineering proportions. 1 unit = 1 metre.
- Create 6–22 objects for a recognizable design.
- Colors: steel=#8a9aaa, concrete=#70787a, glass=#88ccee, wood=#8a5a30, paint=#4a8aff.
- Bridges: box deck, cylinder piers, thin box cables, box towers.
- Buildings: box floors, cylinder columns, plane glass, box roof.
- Gears: cylinder body, smaller cylinders as teeth arranged in radial array.
- Chairs: box seat, cylinder legs.
- Return ONLY the JSON object.`;

  try{
    const resp=await fetch('https://openrouter.ai/api/v1/chat/completions',{
      method:'POST',
      headers:{
        'Authorization':'Bearer '+apiKey,
        'Content-Type':'application/json',
        'HTTP-Referer':'https://ai-cad-studio.streamlit.app',
        'X-Title':'AI CAD Studio Pro',
      },
      body:JSON.stringify({
        model, max_tokens:3000, temperature:0.35,
        messages:[{role:'system',content:sys},{role:'user',content:'Design: '+prompt}],
      }),
    });
    const data=await resp.json();
    if(!resp.ok){
      const e=data.error?.message||resp.statusText;
      body.innerHTML='<div style="color:#cc3030;font-size:11px;">✗ API Error '+resp.status+': '+e+'</div>';
      return setMsg('Generator error '+resp.status);
    }
    let raw=data.choices?.[0]?.message?.content||'';
    let design;
    try{
      raw=raw.replace(/```json|```/g,'').trim();
      // Find first { to last }
      const s=raw.indexOf('{'), e=raw.lastIndexOf('}');
      if(s>=0&&e>s) raw=raw.slice(s,e+1);
      design=JSON.parse(raw);
    }catch(pe){
      body.innerHTML='<div style="color:#cc3030;font-size:11px;">✗ Could not parse JSON.<br><pre style="font-size:9px;white-space:pre-wrap;color:#444;">'+raw.slice(0,500)+'</pre></div>';
      return setMsg('Parse error — try a different model');
    }

    // Build scene
    clearScene();
    const built=[];
    for(const obj of (design.objects||[])){
      const type=obj.type||'box';
      const geo=mkGeo(type);
      const mat=mkMat(obj.color||'#888888', obj.roughness??0.4, obj.metalness??0.2);
      const mesh=new THREE.Mesh(geo,mat);
      mesh.castShadow=true; mesh.receiveShadow=true;
      const [px,py,pz]=obj.position||[0,0,0];
      const [rx,ry,rz]=obj.rotation||[0,0,0];
      const [sx,sy,sz]=obj.scale||[1,1,1];
      mesh.position.set(px,py,pz);
      mesh.rotation.set(rx*Math.PI/180, ry*Math.PI/180, rz*Math.PI/180);
      mesh.scale.set(sx,sy,sz);
      const nm=obj.name||type;
      nameCnt[type]=(nameCnt[type]||0)+1;
      mesh.userData={type,name:nm,layer:'Layer 0',note:obj.note||''};
      scene.add(mesh); objects.push(mesh);
      objMeta.set(mesh,{bbox:null,dimGrp:null,normHelper:null,history:['ai_generated']});
      built.push(nm+' ('+type+')');
    }
    updCount();
    orb.r=35; orb.tx=0; orb.ty=3; orb.tz=0; orb.phi=1.0; orb.theta=0.6;

    body.innerHTML='<div class="ai-tag">'+design.name+'</div>'
      +'<p style="margin-bottom:8px;color:#3a80a0;">'+design.description+'</p>'
      +'<div class="ai-sec">Parts ('+built.length+')</div>'
      +'<ul style="padding-left:12px;margin:4px 0;">'
      +built.map(b=>'<li style="margin:2px 0;color:#2a6080;">'+b+'</li>').join('')
      +'</ul>'
      +'<div class="ai-sec">Design Notes</div>'
      +'<p style="color:#2a6080;font-size:10px;">'+design.notes+'</p>';
    setMsg('Generated: '+design.name+' — '+built.length+' parts · click to select');
  }catch(err){
    body.innerHTML='<div style="color:#cc3030;font-size:11px;">✗ '+err.message+'</div>';
    setMsg('Network error'); console.error(err);
  }
}

// ═══════════════════════════════════════════════════
// AI ANALYZER
// ═══════════════════════════════════════════════════
async function analyzeSelected(){
  if(!selected){setMsg('Select an object first');return;}
  if(!CFG.apiKey){setMsg('No API key in secrets.toml');return;}
  const panel=document.getElementById('ai-analyze-panel');
  const body=document.getElementById('ai-analyze-body');
  panel.style.display='flex';
  body.innerHTML='<div class="ldg"><span>Analyzing</span><span class="dot">■</span><span class="dot">■</span><span class="dot">■</span></div>';
  const bb=new THREE.Box3().setFromObject(selected);
  const sz=new THREE.Vector3(); bb.getSize(sz);
  const mode=document.getElementById('ai-mode').value;
  const model=document.getElementById('ai-model').value;
  const allObjs=objects.map(o=>{
    const ob=new THREE.Box3().setFromObject(o);
    const os=new THREE.Vector3(); ob.getSize(os);
    return o.userData.name+'('+o.userData.type+')@'+o.position.toArray().map(v=>v.toFixed(1)).join(',');
  }).join('; ');
  const modeMap={
    'General Design Review':'Give a concise engineering design review covering geometry, placement, proportions, and assembly role.',
    'Structural Analysis':'Analyze structural properties: stress points, weak regions, support requirements, load paths.',
    'Dimensional Check':'Review proportions. Flag non-standard dimensions. Suggest real-world standard sizes.',
    'GD&T Suggestions':'Suggest GD&T annotations: datums, form tolerances, position tolerances.',
    'Manufacturing Feasibility':'Assess manufacturability: draft angles, undercuts, wall thickness, recommended processes.',
    'FEA Pre-check':'Identify mesh refinement regions, BCs, element type recommendations.',
    'Assembly Notes':'Describe interfaces with adjacent objects. Suggest mate types, fits, sequence.',
  };
  const prompt=`You are a senior mechanical engineer reviewing a CAD part.
SELECTED: ${selected.userData.name} (${selected.userData.type})
Layer: ${selected.userData.layer||'Layer 0'}
Position: ${selected.position.toArray().map(v=>v.toFixed(3)).join(', ')}
Rotation (deg): ${[selected.rotation.x,selected.rotation.y,selected.rotation.z].map(v=>(v*57.3).toFixed(1)).join(', ')}
Bounding box: ${sz.x.toFixed(3)} × ${sz.y.toFixed(3)} × ${sz.z.toFixed(3)} units
Volume (bbox approx): ${(sz.x*sz.y*sz.z).toFixed(4)} u³
Color: #${selected.material.color.getHexString()}
Roughness: ${selected.material.roughness?.toFixed(3)}, Metalness: ${selected.material.metalness?.toFixed(3)}
CAD history: ${(objMeta.get(selected)?.history||[]).join(' → ')}
Note: ${selected.userData.note||'none'}
SCENE (${objects.length} total): ${allObjs}
TASK: ${modeMap[mode]||modeMap['General Design Review']}
${aiDetail==='detailed'?'Provide 4-6 paragraphs.':'Be concise — 2-3 paragraphs.'}`;

  try{
    const resp=await fetch('https://openrouter.ai/api/v1/chat/completions',{
      method:'POST',
      headers:{
        'Authorization':'Bearer '+CFG.apiKey,
        'Content-Type':'application/json',
        'HTTP-Referer':'https://ai-cad-studio.streamlit.app',
        'X-Title':'AI CAD Studio Pro',
      },
      body:JSON.stringify({
        model, max_tokens:aiDetail==='detailed'?900:450, temperature:0.3,
        messages:[{role:'user',content:prompt}],
      }),
    });
    const data=await resp.json();
    if(!resp.ok){
      body.innerHTML='<div class="ai-tag">'+selected.userData.name+'</div>'
        +'<div style="color:#cc3030;font-size:11px;">✗ Error '+resp.status+': '+(data.error?.message||resp.statusText)+'</div>';
      return setMsg('Analyze error '+resp.status);
    }
    const text=data.choices?.[0]?.message?.content||'(no response)';
    const fmt=text.split('\n').filter(l=>l.trim()).map(l=>{
      if(l.match(/^#+\s/)) return '<div class="ai-sec">'+l.replace(/^#+\s/,'')+'</div>';
      return '<p style="margin-bottom:8px">'+l+'</p>';
    }).join('');
    body.innerHTML='<div class="ai-tag">'+selected.userData.name+' · '+mode+'</div>'+fmt;
    setMsg('Analysis complete for '+selected.userData.name);
  }catch(err){
    body.innerHTML='<div style="color:#cc3030;font-size:11px;">✗ '+err.message+'</div>';
    setMsg('Network error'); console.error(err);
  }
}

// ═══════════════════════════════════════════════════
// MOUSE / POINTER
// ═══════════════════════════════════════════════════
const _ray=new THREE.Raycaster();
const _mv=new THREE.Vector2();
function getHits(ev,targets){
  const rc=renderer.domElement.getBoundingClientRect();
  _mv.x=((ev.clientX-rc.left)/rc.width)*2-1;
  _mv.y=-((ev.clientY-rc.top)/rc.height)*2+1;
  _ray.setFromCamera(_mv,cam);
  return _ray.intersectObjects(targets,true);
}

let isOrb=false,isPan=false,isDrag=false;
let lm={x:0,y:0},dm={x:0,y:0};
let dragAxis=null,sp0=null,sr0=null,ss0=null;
let ptrMoved=false;

renderer.domElement.addEventListener('mousedown',e=>{
  dm={x:e.clientX,y:e.clientY}; ptrMoved=false;
  if(selected&&gizmoGroup&&!cadSt.measure&&cadSt.opMode===null){
    const all=[]; gizmoGroup.traverse(c=>{if(c.isMesh||c.isLine)all.push(c);});
    const hits=getHits(e,all);
    if(hits.length){
      let anc=hits[0].object;
      while(anc.parent&&!anc.userData.axis) anc=anc.parent;
      if(anc.userData.axis){
        dragAxis=anc.userData.axis; isDrag=true;
        sp0=selected.position.clone(); sr0=selected.rotation.clone(); ss0=selected.scale.clone();
        lm={x:e.clientX,y:e.clientY}; return;
      }
    }
  }
  if(e.button===0) isOrb=true;
  if(e.button===2) isPan=true;
  lm={x:e.clientX,y:e.clientY};
});

renderer.domElement.addEventListener('mouseup',e=>{
  if(isDrag){
    isDrag=false; dragAxis=null;
    updateBboxes(); updatePropsPanel(selected);
    pushHist(selected,transformMode);
    // Sync sidebar inputs after drag
    if(selected){
      const p=selected.position,r=selected.rotation,s=selected.scale;
      document.getElementById('in-px').value=p.x.toFixed(3);
      document.getElementById('in-py').value=p.y.toFixed(3);
      document.getElementById('in-pz').value=p.z.toFixed(3);
      document.getElementById('in-rx').value=(r.x*180/Math.PI).toFixed(1);
      document.getElementById('in-ry').value=(r.y*180/Math.PI).toFixed(1);
      document.getElementById('in-rz').value=(r.z*180/Math.PI).toFixed(1);
      document.getElementById('in-sx').value=s.x.toFixed(3);
      document.getElementById('in-sy').value=s.y.toFixed(3);
      document.getElementById('in-sz').value=s.z.toFixed(3);
    }
    return;
  }
  isOrb=false; isPan=false;
  if(!ptrMoved&&Math.abs(e.clientX-dm.x)<6&&Math.abs(e.clientY-dm.y)<6&&e.button===0){
    if(cadSt.measure){doMeasure(e);return;}
    const hits=getHits(e,objects);
    const hit=hits.length?hits[0].object:null;
    if(cadSt.opMode==='loft'){
      if(hit&&!cadSt.loftTargets.includes(hit)){
        cadSt.loftTargets.push(hit);
        hit.material.emissive?.setHex(0x0c2438);
        setMsg('LOFT: '+cadSt.loftTargets.length+'/2 selected'+(cadSt.loftTargets.length===2?' — executing…':''));
        if(cadSt.loftTargets.length===2) setTimeout(finishLoft,80);
      }
      return;
    }
    if(cadSt.opMode&&cadSt.opMode.startsWith('bool-')){
      const op=cadSt.opMode.slice(5);
      if(hit&&hit!==cadSt.boolTarget) finishBoolean(op,cadSt.boolTarget,hit);
      return;
    }
    selectObj(hit);
  }
});

renderer.domElement.addEventListener('mousemove',e=>{
  if(Math.abs(e.clientX-dm.x)>4||Math.abs(e.clientY-dm.y)>4) ptrMoved=true;
  // Cursor world pos
  const hits=getHits(e,[...objects,gnd]);
  if(hits.length){
    const hp=hits[0].point;
    let cx=hp.x,cy=hp.y,cz=hp.z;
    if(cadSt.snap){
      cx=Math.round(cx/cadSt.snapSz)*cadSt.snapSz;
      cz=Math.round(cz/cadSt.snapSz)*cadSt.snapSz;
      const sd=document.getElementById('snap-dot');
      sd.style.display='block'; sd.style.left=e.clientX+'px'; sd.style.top=e.clientY+'px';
    } else document.getElementById('snap-dot').style.display='none';
    document.getElementById('hud-cur').textContent=cx.toFixed(2)+', '+cy.toFixed(2)+', '+cz.toFixed(2);
  }

  if(isDrag&&selected&&dragAxis){
    const dx=(e.clientX-lm.x)*0.016, dy=-(e.clientY-lm.y)*0.016;
    const d=Math.abs(dx)>Math.abs(dy)?dx:dy;
    const ax=dragAxis;
    const sn=v=>cadSt.snap?Math.round(v/cadSt.snapSz)*cadSt.snapSz:v;
    if(transformMode==='move'){
      const np=sp0.clone();
      if(ax==='x') np.x=sn(sp0.x+dx*2.4);
      else if(ax==='y') np.y=sn(sp0.y+dy*2.4);
      else if(ax==='z') np.z=sn(sp0.z+dx*2.4);
      else if(ax==='xz'){np.x=sn(sp0.x+dx*2.4);np.z=sn(sp0.z+dx*2.4);}
      else if(ax==='xy'){np.x=sn(sp0.x+dx*2.4);np.y=sn(sp0.y+dy*2.4);}
      else if(ax==='yz'){np.y=sn(sp0.y+dy*2.4);np.z=sn(sp0.z+dx*2.4);}
      selected.position.copy(np);
    } else if(transformMode==='rotate'){
      const nr=sr0.clone();
      if(ax==='x') nr.x=sr0.x+d*2.6;
      else if(ax==='y') nr.y=sr0.y+d*2.6;
      else nr.z=sr0.z+d*2.6;
      selected.rotation.copy(nr);
    } else {
      const sc=ss0.clone(),f=1+d*1.3;
      if(ax==='xyz'){sc.x=Math.max(0.001,ss0.x*f);sc.y=Math.max(0.001,ss0.y*f);sc.z=Math.max(0.001,ss0.z*f);}
      else if(ax==='x') sc.x=Math.max(0.001,ss0.x*f);
      else if(ax==='y') sc.y=Math.max(0.001,ss0.y*f);
      else sc.z=Math.max(0.001,ss0.z*f);
      selected.scale.copy(sc);
    }
    syncGizmo(); updateHUD();
    lm={x:e.clientX,y:e.clientY}; return;
  }
  if(isOrb){
    orb.theta-=(e.clientX-lm.x)*0.006;
    orb.phi-=(e.clientY-lm.y)*0.006;
    orb.phi=Math.max(0.04,Math.min(Math.PI-0.04,orb.phi));
  }
  if(isPan){
    const spd=0.009*(orb.r/12);
    const fwd=new THREE.Vector3(orb.tx-cam.position.x,0,orb.tz-cam.position.z).normalize();
    const right=new THREE.Vector3().crossVectors(fwd,new THREE.Vector3(0,1,0)).normalize();
    orb.tx-=right.x*(e.clientX-lm.x)*spd;
    orb.tz-=right.z*(e.clientX-lm.x)*spd;
    orb.ty+=(e.clientY-lm.y)*spd;
  }
  lm={x:e.clientX,y:e.clientY};
});

renderer.domElement.addEventListener('wheel',e=>{
  orb.r*=1+e.deltaY*0.0007;
  orb.r=Math.max(1,Math.min(500,orb.r));
},{passive:true});
renderer.domElement.addEventListener('contextmenu',e=>e.preventDefault());

// Keyboard
document.addEventListener('keydown',e=>{
  if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA') return;
  const k=e.key.toLowerCase();
  if(k==='x'&&!e.ctrlKey) analyzeSelected();
  if(k==='e'&&!e.ctrlKey) cadExtrude();
  if(k==='escape'){
    selectObj(null);
    cadSt.opMode=null; cadSt.loftTargets=[]; cadSt.boolTarget=null;
    setOpOverlay(null);
    document.getElementById('sb-mode').textContent='NAVIGATE';
    document.getElementById('sb-mode').className='sc';
  }
  if(k==='delete'||k==='backspace'){e.preventDefault();deleteSel();}
  if(k==='d'&&!e.ctrlKey) duplicate();
  if(k==='f') frameSelected();
  if(k==='g'){cadSt.snap=!cadSt.snap;setMsg('Snap '+(cadSt.snap?'ON':'OFF'));}
  if(k==='w') toggleWire();
  if(k==='m') toggleMeasure();
});

function setMsg(msg){document.getElementById('sb-msg').textContent=msg;}

// Render loop
(function animate(){
  requestAnimationFrame(animate);
  applyOrbit();
  if(selected&&gizmoGroup) syncGizmo();
  updateBboxes();
  updateHUD();
  renderer.render(scene,cam);
})();

onResize();
</script>
</body>
</html>"""

# Inject API key and model into the self-contained HTML
HTML = HTML.replace('CFG.apiKey       = `""" + OPENROUTER_API_KEY + r"""`;',
                    f'CFG.apiKey       = `{OPENROUTER_API_KEY}`;')
HTML = HTML.replace('CFG.modelDefault = `""" + OPENROUTER_MODEL_DEFAULT + r"""`;',
                    f'CFG.modelDefault = `{OPENROUTER_MODEL_DEFAULT}`;')

components.html(HTML, height=820, scrolling=False)