import streamlit as st
import streamlit.components.v1 as components

# ============================================================
#  INSERT YOUR ANTHROPIC API KEY HERE
# ============================================================
API_KEY = "your-api-key-here"
# ============================================================

st.set_page_config(page_title="AI 3D Studio", layout="wide", page_icon="🧊")

st.markdown("""
<style>
body, .stApp { background:#0d1117 !important; color:#e6edf3; }
[data-testid="stSidebar"] { background:#161b22 !important; border-right:1px solid #30363d; }
[data-testid="stSidebar"] label,[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,[data-testid="stSidebar"] div { color:#c9d1d9 !important; }
.stButton > button {
  background:#21262d; color:#c9d1d9; border:1px solid #30363d;
  border-radius:6px; font-size:13px; width:100%; margin:2px 0; transition:all 0.15s;
}
.stButton > button:hover { background:#1f6feb; border-color:#1f6feb; color:#fff; }
footer, header, #MainMenu { visibility:hidden; }
.block-container { padding-top:0.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧊 AI 3D Studio")
    st.markdown("---")
    st.markdown("### ➕ Add Shape")
    c1, c2 = st.columns(2)
    with c1:
        add_cube     = st.button("⬛ Cube")
        add_cylinder = st.button("🔵 Cylinder")
        add_cone     = st.button("🔺 Cone")
    with c2:
        add_sphere   = st.button("⚪ Sphere")
        add_torus    = st.button("⭕ Torus")
        add_plane    = st.button("▭ Plane")

    st.markdown("---")
    st.markdown("### 🎮 Transform Mode")
    mode = st.radio("", ["Move","Rotate","Scale"], horizontal=True, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### 🗑️ Scene")
    delete_sel = st.button("🗑 Delete Selected")
    clear_all  = st.button("✕ Clear All")

    st.markdown("---")
    st.markdown("### 🎨 Color")
    color_pick  = st.color_picker("Pick color", "#4a9eff")
    apply_color = st.button("Apply Color")

    st.markdown("---")
    st.markdown("### 🤖 AI Settings")
    analysis_mode = st.selectbox("Analysis type", [
        "General Design Review",
        "Structural Analysis",
        "Aesthetic & Composition",
        "Optimization Suggestions",
        "Architecture Critique",
    ])
    st.markdown("""
    <div style='background:#1f6feb22;border:1px solid #1f6feb44;border-radius:6px;
    padding:10px 12px;font-size:12px;color:#58a6ff;margin-top:8px;'>
    Press <b>X</b> on your keyboard to analyze the selected object with Claude.
    </div>
    """, unsafe_allow_html=True)

# ── JS command for sidebar buttons ───────────────────────────
js_cmd = "null"
if add_cube:      js_cmd = "'addShape:cube'"
elif add_sphere:  js_cmd = "'addShape:sphere'"
elif add_cylinder:js_cmd = "'addShape:cylinder'"
elif add_cone:    js_cmd = "'addShape:cone'"
elif add_torus:   js_cmd = "'addShape:torus'"
elif add_plane:   js_cmd = "'addShape:plane'"
elif delete_sel:  js_cmd = "'deleteSelected'"
elif clear_all:   js_cmd = "'clearScene'"
elif apply_color: js_cmd = f"'setColor:{color_pick}'"

mode_js = {"Move":"move","Rotate":"rotate","Scale":"scale"}[mode]

# ── The full self-contained HTML app ─────────────────────────
HTML = f"""<!DOCTYPE html>
<html>
<head>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0d1117; overflow:hidden; font-family:monospace; user-select:none; }}
canvas {{ display:block; }}

#hud {{
  position:absolute; top:10px; left:10px;
  background:#161b2299; border:1px solid #30363d; border-radius:6px;
  padding:8px 13px; font-size:10px; color:#8b949e; line-height:2;
  pointer-events:none;
}}
#status {{
  position:absolute; bottom:10px; left:10px; right:10px; text-align:center;
  background:#161b2299; border:1px solid #30363d; border-radius:6px;
  padding:5px 14px; font-size:11px; color:#c9d1d9; pointer-events:none;
}}

/* AI Panel overlay */
#ai-panel {{
  position:absolute; top:10px; right:10px; width:340px;
  background:#161b22ee; border:1px solid #30363d; border-radius:8px;
  display:none; flex-direction:column; max-height:calc(100vh - 80px);
  box-shadow: 0 8px 32px #00000088;
}}
#ai-header {{
  display:flex; align-items:center; justify-content:space-between;
  padding:10px 14px; border-bottom:1px solid #30363d;
}}
#ai-header span {{ color:#58a6ff; font-size:11px; letter-spacing:0.08em; text-transform:uppercase; }}
#ai-close {{
  background:none; border:none; color:#8b949e; cursor:pointer;
  font-size:16px; padding:0 4px; line-height:1;
}}
#ai-close:hover {{ color:#e6edf3; }}
#ai-body {{
  padding:14px; overflow-y:auto; flex:1;
  font-size:12px; color:#c9d1d9; line-height:1.75;
}}
#ai-body .obj-tag {{
  background:#1f6feb22; border:1px solid #1f6feb44; border-radius:4px;
  padding:3px 8px; font-size:10px; color:#58a6ff; margin-bottom:10px; display:inline-block;
}}
#ai-body .loading {{
  display:flex; align-items:center; gap:8px; color:#8b949e;
}}
#ai-body .dot {{ animation:blink 1.2s infinite; }}
#ai-body .dot:nth-child(2) {{ animation-delay:0.2s; }}
#ai-body .dot:nth-child(3) {{ animation-delay:0.4s; }}
@keyframes blink {{ 0%,80%,100%{{opacity:0;}} 40%{{opacity:1;}} }}

#x-hint {{
  position:absolute; bottom:46px; right:10px;
  background:#1f6feb22; border:1px solid #1f6feb44; border-radius:5px;
  padding:4px 10px; font-size:10px; color:#58a6ff; pointer-events:none;
  transition:opacity 0.3s;
}}
</style>
</head>
<body>

<div id="hud">
  🖱 Left-drag · Orbit &nbsp;|&nbsp; Right-drag · Pan &nbsp;|&nbsp; Scroll · Zoom<br>
  Click object · Select &nbsp;|&nbsp; Drag arrows · Transform &nbsp;|&nbsp; <b>X</b> · Analyze with AI
</div>
<div id="status">Ready — add shapes from the sidebar, press X to analyze</div>
<div id="x-hint">Press <b>X</b> to analyze selected object</div>

<!-- AI Result Panel -->
<div id="ai-panel">
  <div id="ai-header">
    <span>🤖 Claude Analysis</span>
    <button id="ai-close" onclick="closeAI()">✕</button>
  </div>
  <div id="ai-body">
    <div class="loading">
      <span>Analyzing</span>
      <span class="dot">●</span><span class="dot">●</span><span class="dot">●</span>
    </div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const API_KEY = "{API_KEY}";
const ANALYSIS_MODE = "{analysis_mode}";

// ── Renderer ──────────────────────────────────────────────────
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setPixelRatio(devicePixelRatio);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);
function resize() {{
  renderer.setSize(innerWidth, innerHeight);
  cam.aspect = innerWidth / innerHeight;
  cam.updateProjectionMatrix();
}}
window.addEventListener('resize', resize);

// ── Scene ─────────────────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0d1117);
scene.fog = new THREE.FogExp2(0x0d1117, 0.015);

// ── Camera ────────────────────────────────────────────────────
const cam = new THREE.PerspectiveCamera(55, innerWidth/innerHeight, 0.1, 300);
const orb = {{theta:0.6, phi:1.1, r:14, tx:0, ty:0, tz:0}};
function applyCam() {{
  cam.position.set(
    orb.tx + orb.r*Math.sin(orb.phi)*Math.sin(orb.theta),
    orb.ty + orb.r*Math.cos(orb.phi),
    orb.tz + orb.r*Math.sin(orb.phi)*Math.cos(orb.theta)
  );
  cam.lookAt(orb.tx, orb.ty, orb.tz);
}}

// ── Lights ────────────────────────────────────────────────────
scene.add(new THREE.AmbientLight(0x334466, 0.9));
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(10,18,8); sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
['left','right','top','bottom'].forEach((s,i) => sun.shadow.camera[s] = [-20,20,20,-20][i]);
scene.add(sun);
const fill = new THREE.DirectionalLight(0x4488ff, 0.4);
fill.position.set(-8,4,-6); scene.add(fill);

// ── Grid ─────────────────────────────────────────────────────
scene.add(new THREE.GridHelper(30,30,0x30363d,0x1a1f27));
const gnd = new THREE.Mesh(
  new THREE.PlaneGeometry(100,100),
  new THREE.MeshBasicMaterial({{visible:false, side:THREE.DoubleSide}})
);
gnd.rotation.x = -Math.PI/2; gnd.name='_ground'; scene.add(gnd);

// ── State ─────────────────────────────────────────────────────
let objects=[], selected=null, transformMode='{mode_js}', colorIdx=0;
const COLORS=[0x4a9eff,0xff6b6b,0x6bffb8,0xffd93d,0xa78bfa,0xfb923c,0x34d399,0xf472b6];
const nameCnt={{}};

// ── Gizmo ─────────────────────────────────────────────────────
let gizmoGroup=null;
const AX={{x:0xff4444,y:0x44ff44,z:0x4488ff}};
function buildGizmo() {{
  if(gizmoGroup) scene.remove(gizmoGroup);
  gizmoGroup = new THREE.Group(); gizmoGroup.name='_gizmo';
  ['x','y','z'].forEach(ax => {{
    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.05,1.5,8), new THREE.MeshBasicMaterial({{color:AX[ax],depthTest:false}}));
    const tip   = new THREE.Mesh(new THREE.ConeGeometry(0.13,0.38,8), new THREE.MeshBasicMaterial({{color:AX[ax],depthTest:false}}));
    tip.position.y = 0.94;
    const arr = new THREE.Group(); arr.add(shaft,tip); arr.userData.axis=ax;
    if(ax==='x') {{ arr.rotation.z=-Math.PI/2; arr.position.x=0.95; }}
    if(ax==='y') {{ arr.position.y=0.95; }}
    if(ax==='z') {{ arr.rotation.x=Math.PI/2; arr.position.z=0.95; }}
    gizmoGroup.add(arr);
  }});
  scene.add(gizmoGroup);
}}
function syncGizmo() {{
  if(!selected||!gizmoGroup) return;
  gizmoGroup.position.copy(selected.position);
  gizmoGroup.scale.setScalar(Math.max(...selected.scale.toArray())*0.55+0.5);
}}

// ── Shapes ────────────────────────────────────────────────────
const GEOS = {{
  cube:     () => new THREE.BoxGeometry(1.2,1.2,1.2),
  sphere:   () => new THREE.SphereGeometry(0.75,32,32),
  cylinder: () => new THREE.CylinderGeometry(0.6,0.6,1.5,32),
  cone:     () => new THREE.ConeGeometry(0.7,1.5,32),
  torus:    () => new THREE.TorusGeometry(0.65,0.22,16,64),
  plane:    () => new THREE.PlaneGeometry(2,2),
}};

function addShape(type) {{
  nameCnt[type] = (nameCnt[type]||0)+1;
  const mat = new THREE.MeshStandardMaterial({{color:COLORS[colorIdx++%COLORS.length],roughness:0.38,metalness:0.18}});
  const mesh = new THREE.Mesh(GEOS[type](), mat);
  mesh.castShadow=true; mesh.receiveShadow=true;
  const a=Math.random()*Math.PI*2, r=Math.random()*3;
  mesh.position.set(Math.cos(a)*r, 0.8, Math.sin(a)*r);
  mesh.userData = {{type, name: type+'_'+nameCnt[type]}};
  scene.add(mesh); objects.push(mesh);
  selectObj(mesh);
  setStatus('Added ' + mesh.userData.name + ' — press X to analyze');
}}

function selectObj(obj) {{
  if(selected && selected!==obj) selected.material.emissive.setHex(0x000000);
  selected = obj;
  if(selected) {{
    selected.material.emissive.setHex(0x223355);
    buildGizmo(); syncGizmo();
    const p = selected.position;
    setStatus('Selected: ' + selected.userData.name + ' | Press X to analyze with AI');
    document.getElementById('x-hint').style.opacity='1';
  }} else {{
    if(gizmoGroup) {{ scene.remove(gizmoGroup); gizmoGroup=null; }}
    document.getElementById('x-hint').style.opacity='0';
  }}
}}

function deleteSelected() {{
  if(!selected) return setStatus('Nothing selected');
  scene.remove(selected); objects=objects.filter(o=>o!==selected);
  if(gizmoGroup) {{ scene.remove(gizmoGroup); gizmoGroup=null; }}
  selected=null; setStatus('Deleted');
}}

function clearScene() {{
  objects.forEach(o=>scene.remove(o)); objects=[]; colorIdx=0;
  Object.keys(nameCnt).forEach(k=>delete nameCnt[k]);
  if(gizmoGroup) {{ scene.remove(gizmoGroup); gizmoGroup=null; }}
  selected=null; closeAI(); setStatus('Scene cleared');
}}

function setColor(hex) {{
  if(!selected) return setStatus('Select an object first');
  selected.material.color.set(hex); setStatus('Color applied');
}}

// ── AI Analysis (called on X key press) ──────────────────────
function closeAI() {{
  document.getElementById('ai-panel').style.display='none';
}}

async function analyzeSelected() {{
  if(!selected) return setStatus('Select an object first, then press X');

  const panel = document.getElementById('ai-panel');
  const body  = document.getElementById('ai-body');

  // Show panel with loading state
  panel.style.display = 'flex';
  body.innerHTML = `
    <div class="obj-tag">${{selected.userData.name}} · ${{selected.userData.type}}</div>
    <div class="loading">
      <span>Analyzing</span>
      <span class="dot">●</span><span class="dot">●</span><span class="dot">●</span>
    </div>`;

  setStatus('Sending ' + selected.userData.name + ' to Claude...');

  const c = selected.material.color;
  const obj = {{
    name:     selected.userData.name,
    type:     selected.userData.type,
    position: selected.position.toArray().map(v=>+v.toFixed(3)),
    rotation: [selected.rotation.x, selected.rotation.y, selected.rotation.z].map(v=>+v.toFixed(3)),
    scale:    selected.scale.toArray().map(v=>+v.toFixed(3)),
    color:    '#'+c.getHexString(),
    total_objects_in_scene: objects.length,
  }};

  const modePrompts = {{
    "General Design Review":    "Give a concise design review of this selected 3D object, covering its placement, scale, and role in the overall scene.",
    "Structural Analysis":      "Analyze the structural placement and spatial logic of this object. Is it positioned sensibly?",
    "Aesthetic & Composition":  "Evaluate the aesthetic of this object — color, scale, and its visual contribution to the scene.",
    "Optimization Suggestions": "Give specific improvements for this object: position, scale, color, or shape type.",
    "Architecture Critique":    "Critique this object as an architect would: proportions, placement, and form.",
  }};

  const task = modePrompts[ANALYSIS_MODE] || modePrompts["General Design Review"];

  const prompt = `You are an expert 3D designer and design critic.

Selected object:
  Name: ${{obj.name}}
  Type: ${{obj.type}}
  Position: ${{JSON.stringify(obj.position)}}
  Rotation (radians): ${{JSON.stringify(obj.rotation)}}
  Scale: ${{JSON.stringify(obj.scale)}}
  Color: ${{obj.color}}
  Total objects in scene: ${{obj.total_objects_in_scene}}

Task: ${{task}}

Be concise and specific. 3-5 short paragraphs. Reference the actual object name and properties.`;

  try {{
    const resp = await fetch("https://api.anthropic.com/v1/messages", {{
      method: "POST",
      headers: {{
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      }},
      body: JSON.stringify({{
        model: "claude-opus-4-6",
        max_tokens: 500,
        messages: [{{ role: "user", content: prompt }}],
      }}),
    }});

    const data = await resp.json();

    if(!resp.ok) {{
      const errMsg = data.error?.message || resp.statusText;
      body.innerHTML = `
        <div class="obj-tag">${{obj.name}}</div>
        <div style="color:#ff6b6b;font-size:12px;">
          ❌ API Error ${{resp.status}}: ${{errMsg}}
          ${{resp.status===401 ? '<br><br>Check that API_KEY is set correctly at the top of app.py.' : ''}}
        </div>`;
      return setStatus('API error — check the panel');
    }}

    const text = data.content[0].text;

    // Format response with paragraphs
    const formatted = text.split('\\n').filter(l=>l.trim()).map(l =>
      `<p style="margin-bottom:10px">${{l}}</p>`
    ).join('');

    body.innerHTML = `
      <div class="obj-tag">${{obj.name}} · ${{obj.type}} · ${{obj.color}}</div>
      ${{formatted}}`;

    setStatus('Analysis complete for ' + obj.name + ' — press X anytime to re-analyze');

  }} catch(err) {{
    body.innerHTML = `
      <div class="obj-tag">${{obj.name}}</div>
      <div style="color:#ff6b6b;font-size:12px;">
        ❌ Network error: ${{err.message}}<br><br>
        Make sure the Anthropic API is reachable.
      </div>`;
    setStatus('Network error — check console');
    console.error(err);
  }}
}}

// ── Keyboard shortcut: X ──────────────────────────────────────
document.addEventListener('keydown', e => {{
  if(e.key.toLowerCase() === 'x' && !e.ctrlKey && !e.metaKey) {{
    analyzeSelected();
  }}
  if(e.key === 'Escape') closeAI();
  if(e.key === 'Delete' || e.key === 'Backspace') deleteSelected();
}});

// ── Raycaster ─────────────────────────────────────────────────
const ray=new THREE.Raycaster(), mpos=new THREE.Vector2();
function getHits(ev, targets) {{
  const rc = renderer.domElement.getBoundingClientRect();
  mpos.x = ((ev.clientX-rc.left)/rc.width)*2-1;
  mpos.y = -((ev.clientY-rc.top)/rc.height)*2+1;
  ray.setFromCamera(mpos, cam);
  return ray.intersectObjects(targets, true);
}}

// ── Mouse ─────────────────────────────────────────────────────
let isOrb=false, isPan=false, isDrag=false;
let lm={{x:0,y:0}}, dm={{x:0,y:0}};
let dragAxis=null, sp=null, sr=null, ss=null;

renderer.domElement.addEventListener('mousedown', e => {{
  dm={{x:e.clientX,y:e.clientY}};
  if(selected && gizmoGroup) {{
    const all=[]; gizmoGroup.traverse(c=>{{if(c.isMesh)all.push(c);}});
    const hits=getHits(e,all);
    if(hits.length>0) {{
      let anc=hits[0].object;
      while(anc.parent && !anc.userData.axis) anc=anc.parent;
      dragAxis=anc.userData.axis; isDrag=true;
      sp=selected.position.clone(); sr=selected.rotation.clone(); ss=selected.scale.clone();
      lm={{x:e.clientX,y:e.clientY}}; return;
    }}
  }}
  if(e.button===0) isOrb=true;
  if(e.button===2) isPan=true;
  lm={{x:e.clientX,y:e.clientY}};
}});

renderer.domElement.addEventListener('mouseup', e => {{
  if(isDrag) {{ isDrag=false; dragAxis=null; return; }}
  isOrb=false; isPan=false;
  if(Math.abs(e.clientX-dm.x)<5 && Math.abs(e.clientY-dm.y)<5 && e.button===0) {{
    const hits=getHits(e,objects);
    selectObj(hits.length ? hits[0].object : null);
  }}
}});

renderer.domElement.addEventListener('mousemove', e => {{
  if(isDrag && selected && dragAxis) {{
    const dx=(e.clientX-lm.x)*0.02, dy=-(e.clientY-lm.y)*0.02;
    const d=Math.abs(dx)>Math.abs(dy)?dx:dy;
    if(transformMode==='move') {{
      const p=sp.clone();
      if(dragAxis==='x') p.x+=dx*2.2;
      if(dragAxis==='y') p.y+=dy*2.2;
      if(dragAxis==='z') p.z+=dx*2.2;
      selected.position.copy(p);
    }} else if(transformMode==='rotate') {{
      const r=sr.clone();
      if(dragAxis==='x') r.x+=d*3;
      if(dragAxis==='y') r.y+=d*3;
      if(dragAxis==='z') r.z+=d*3;
      selected.rotation.copy(r);
    }} else if(transformMode==='scale') {{
      const sc=ss.clone(), f=1+d*1.5;
      if(dragAxis==='x') sc.x=Math.max(0.05,ss.x*f);
      if(dragAxis==='y') sc.y=Math.max(0.05,ss.y*f);
      if(dragAxis==='z') sc.z=Math.max(0.05,ss.z*f);
      selected.scale.copy(sc);
    }}
    syncGizmo(); lm={{x:e.clientX,y:e.clientY}}; return;
  }}
  if(isOrb) {{
    orb.theta -= (e.clientX-lm.x)*0.007;
    orb.phi   -= (e.clientY-lm.y)*0.007;
    orb.phi = Math.max(0.08, Math.min(Math.PI-0.08, orb.phi));
  }}
  if(isPan) {{
    const spd=0.012*(orb.r/10);
    const right=new THREE.Vector3().crossVectors(
      new THREE.Vector3(Math.sin(orb.phi)*Math.sin(orb.theta),Math.cos(orb.phi),Math.sin(orb.phi)*Math.cos(orb.theta)),
      new THREE.Vector3(0,1,0)
    ).normalize();
    orb.tx -= right.x*(e.clientX-lm.x)*spd;
    orb.tz -= right.z*(e.clientX-lm.x)*spd;
    orb.ty += (e.clientY-lm.y)*spd;
  }}
  lm={{x:e.clientX,y:e.clientY}};
}});

renderer.domElement.addEventListener('wheel', e => {{
  orb.r *= 1+e.deltaY*0.001; orb.r=Math.max(2,Math.min(80,orb.r));
}}, {{passive:true}});
renderer.domElement.addEventListener('contextmenu', e=>e.preventDefault());

function setStatus(msg) {{ document.getElementById('status').innerText=msg; }}

// ── Handle sidebar button commands ────────────────────────────
(function() {{
  const cmd = {js_cmd};
  if(!cmd || cmd==='null') return;
  if(cmd.startsWith('addShape:')) {{ addShape(cmd.split(':')[1]); return; }}
  if(cmd==='deleteSelected') {{ deleteSelected(); return; }}
  if(cmd==='clearScene') {{ clearScene(); return; }}
  if(cmd.startsWith('setColor:')) {{ setColor(cmd.split(':')[1]); return; }}
}})();

// ── Render loop ───────────────────────────────────────────────
(function animate() {{
  requestAnimationFrame(animate);
  applyCam();
  if(selected && gizmoGroup) syncGizmo();
  renderer.render(scene, cam);
}})();

resize();
</script>
</body>
</html>"""

st.markdown("## 🧊 AI 3D Studio")
components.html(HTML, height=700, scrolling=False)
st.caption("Click a shape to select it, then press **X** to analyze with Claude. Press **Esc** to close the panel.")