import streamlit as st
import streamlit.components.v1 as components
import json, requests

# ── Read API key from Streamlit secrets ───────────────────────
# In Streamlit Cloud: go to App Settings → Secrets and add:
#   OPENAI_API_KEY = "sk-..."
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    API_KEY = ""

st.set_page_config(page_title="CAD AI Studio", layout="wide", page_icon="🔩")

st.markdown("""
<style>
body, .stApp { background:#0d1117 !important; color:#e6edf3; }
[data-testid="stSidebar"] { background:#161b22 !important; border-right:1px solid #30363d; }
[data-testid="stSidebar"] * { color:#c9d1d9 !important; }
.stButton > button {
  background:#21262d !important; color:#c9d1d9 !important;
  border:1px solid #30363d !important; border-radius:6px !important;
  font-size:12px !important; width:100% !important;
  margin:2px 0 !important; transition:all 0.15s !important;
}
.stButton > button:hover { background:#1f6feb !important; border-color:#1f6feb !important; color:#fff !important; }
footer, header, #MainMenu { visibility:hidden; }
.block-container { padding-top:0.5rem !important; }
div[data-testid="stSelectbox"] > div > div { background:#0d1117 !important; color:#c9d1d9 !important; }
div[data-testid="stNumberInput"] input { background:#0d1117 !important; color:#c9d1d9 !important; border:1px solid #30363d !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔩 CAD AI Studio")
    if not API_KEY:
        st.error("⚠ Set OPENAI_API_KEY in Streamlit Secrets (App Settings → Secrets)")
    else:
        st.success("✓ OpenAI key loaded from secrets")
    st.markdown("---")

    # Primitives
    st.markdown("### ➕ Primitives")
    c1,c2 = st.columns(2)
    with c1:
        add_cube      = st.button("⬛ Box")
        add_cylinder  = st.button("🔵 Cylinder")
        add_cone      = st.button("🔺 Cone")
        add_wedge     = st.button("◺ Wedge")
    with c2:
        add_sphere    = st.button("⚪ Sphere")
        add_torus     = st.button("⭕ Torus")
        add_pipe      = st.button("⬤ Pipe")
        add_pyramid   = st.button("△ Pyramid")

    st.markdown("---")

    # CAD ops
    st.markdown("### 🔧 CAD Operations")
    c3,c4 = st.columns(2)
    with c3:
        do_union      = st.button("∪ Union")
        do_extrude    = st.button("↑ Extrude")
        do_mirror_x   = st.button("⟺ Mirror X")
    with c4:
        do_subtract   = st.button("∖ Subtract")
        do_duplicate  = st.button("⧉ Duplicate")
        do_mirror_y   = st.button("⟺ Mirror Y")

    st.markdown("---")

    # Transform
    st.markdown("### 🎮 Transform")
    mode = st.radio("", ["Move","Rotate","Scale"], horizontal=True, label_visibility="collapsed")

    st.markdown("---")

    # Precise input
    st.markdown("### 📐 Precise Transform")
    px = st.number_input("X", value=0.0, step=0.5, format="%.2f", key="px")
    py = st.number_input("Y", value=0.0, step=0.5, format="%.2f", key="py")
    pz = st.number_input("Z", value=0.0, step=0.5, format="%.2f", key="pz")
    apply_pos = st.button("Apply Position")
    sx2 = st.number_input("Scale X", value=1.0, step=0.1, format="%.2f", key="sx2")
    sy2 = st.number_input("Scale Y", value=1.0, step=0.1, format="%.2f", key="sy2")
    sz2 = st.number_input("Scale Z", value=1.0, step=0.1, format="%.2f", key="sz2")
    apply_scale = st.button("Apply Scale")

    st.markdown("---")

    # Grid / snapping
    st.markdown("### 📏 Grid & Snap")
    snap_on   = st.checkbox("Snap to Grid", value=True)
    grid_size = st.selectbox("Grid Size", [0.25, 0.5, 1.0, 2.0], index=2)

    st.markdown("---")

    # Appearance
    st.markdown("### 🎨 Appearance")
    color_pick  = st.color_picker("Color", "#4a9eff")
    apply_color = st.button("Apply Color")
    wireframe   = st.checkbox("Wireframe mode")

    st.markdown("---")

    # Scene
    st.markdown("### 🗑 Scene")
    delete_sel  = st.button("🗑 Delete Selected")
    clear_all   = st.button("✕ Clear All")

    st.markdown("---")

    # AI
    st.markdown("### 🤖 AI Analysis")
    analysis_mode = st.selectbox("Mode", [
        "General Design Review",
        "Structural Analysis",
        "Aesthetic & Composition",
        "CAD Optimization",
        "Manufacturability Check",
        "Architecture Critique",
    ], label_visibility="collapsed")
    if API_KEY:
        st.markdown("""<div style='background:#1f6feb22;border:1px solid #1f6feb55;
        border-radius:6px;padding:8px 11px;font-size:11px;color:#58a6ff;'>
        Click an object → <b>Analyze (X)</b> to get AI feedback</div>""",
        unsafe_allow_html=True)

# ── Build JS command ──────────────────────────────────────────
js_cmd = "null"
if add_cube:     js_cmd = "'add:box'"
elif add_sphere: js_cmd = "'add:sphere'"
elif add_cylinder:js_cmd= "'add:cylinder'"
elif add_cone:   js_cmd = "'add:cone'"
elif add_torus:  js_cmd = "'add:torus'"
elif add_wedge:  js_cmd = "'add:wedge'"
elif add_pipe:   js_cmd = "'add:pipe'"
elif add_pyramid:js_cmd = "'add:pyramid'"
elif do_union:   js_cmd = "'cad:union'"
elif do_subtract:js_cmd = "'cad:subtract'"
elif do_extrude: js_cmd = "'cad:extrude'"
elif do_duplicate:js_cmd= "'cad:duplicate'"
elif do_mirror_x:js_cmd = "'cad:mirrorX'"
elif do_mirror_y:js_cmd = "'cad:mirrorY'"
elif delete_sel: js_cmd = "'delete'"
elif clear_all:  js_cmd = "'clear'"
elif apply_color:js_cmd = f"'color:{color_pick}'"
elif apply_pos:  js_cmd = f"'pos:{px},{py},{pz}'"
elif apply_scale:js_cmd = f"'scale:{sx2},{sy2},{sz2}'"

mode_js   = {"Move":"move","Rotate":"rotate","Scale":"scale"}[mode]
snap_js   = "true" if snap_on else "false"
grid_js   = str(grid_size)
wire_js   = "true" if wireframe else "false"

# ── AI analysis (runs in Python on the server) ────────────────
if "ai_result"  not in st.session_state: st.session_state.ai_result  = ""
if "ai_obj"     not in st.session_state: st.session_state.ai_obj     = ""
if "trigger_ai" not in st.session_state: st.session_state.trigger_ai = False

sel_raw = st.query_params.get("analyze", "")
if sel_raw and sel_raw != st.session_state.ai_obj:
    st.session_state.ai_obj     = sel_raw
    st.session_state.trigger_ai = True

if st.session_state.trigger_ai and API_KEY:
    st.session_state.trigger_ai = False
    try:
        obj = json.loads(sel_raw)
        prompts = {
            "General Design Review":     "Give a concise design review: placement, scale, role in scene.",
            "Structural Analysis":       "Analyze structural integrity and spatial logic.",
            "Aesthetic & Composition":   "Evaluate color, scale, visual contribution.",
            "CAD Optimization":          "Give specific CAD improvements: geometry, scale, constraints.",
            "Manufacturability Check":   "Assess how manufacturable this shape is. Note concerns.",
            "Architecture Critique":     "Critique as an architect: proportions, placement, form.",
        }
        prompt = f"""You are an expert CAD designer and design critic.
Selected object:
  Name:     {obj.get('name')}
  Type:     {obj.get('type')}
  Position: {obj.get('position')}
  Rotation: {obj.get('rotation')} radians
  Scale:    {obj.get('scale')}
  Color:    {obj.get('color')}
  Scene:    {obj.get('total')} total objects

Task: {prompts.get(analysis_mode, prompts["General Design Review"])}
Be specific, reference actual values, 3-4 short paragraphs."""

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"model": "gpt-4o-mini", "max_tokens": 500,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=30
        )
        d = r.json()
        if r.status_code != 200:
            st.session_state.ai_result = f"ERROR:{d.get('error',{}).get('message','Unknown error')}"
        else:
            st.session_state.ai_result = d["choices"][0]["message"]["content"]
    except Exception as e:
        st.session_state.ai_result = f"ERROR:{e}"

ai_result_js = json.dumps(st.session_state.ai_result)
ai_obj_js    = json.dumps(st.session_state.ai_obj)

# ── Viewport HTML/JS ──────────────────────────────────────────
HTML = f"""<!DOCTYPE html><html><head>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#0d1117;overflow:hidden;font-family:monospace;user-select:none;}}
canvas{{display:block;}}
#hud{{position:absolute;top:10px;left:10px;background:#161b2299;border:1px solid #30363d;
  border-radius:6px;padding:8px 13px;font-size:10px;color:#8b949e;line-height:2;pointer-events:none;}}
#status{{position:absolute;bottom:60px;left:10px;right:10px;text-align:center;
  background:#161b2299;border:1px solid #30363d;border-radius:6px;
  padding:5px 14px;font-size:11px;color:#c9d1d9;pointer-events:none;}}
#analyze-btn{{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);
  background:#1f6feb;color:#fff;border:none;border-radius:6px;
  padding:9px 28px;font-size:13px;font-family:monospace;cursor:pointer;
  transition:all 0.15s;display:none;}}
#analyze-btn:hover{{background:#388bfd;}}
#dims{{position:absolute;top:10px;right:10px;background:#161b2299;
  border:1px solid #30363d;border-radius:6px;padding:8px 12px;
  font-size:10px;color:#8b949e;display:none;line-height:1.8;}}
#ai-panel{{position:absolute;top:10px;right:10px;width:310px;
  background:#161b22f2;border:1px solid #30363d;border-radius:8px;
  display:none;flex-direction:column;max-height:calc(100% - 80px);
  box-shadow:0 8px 32px #00000099;}}
#ai-hdr{{display:flex;align-items:center;justify-content:space-between;
  padding:10px 14px;border-bottom:1px solid #30363d;}}
#ai-hdr span{{color:#58a6ff;font-size:11px;letter-spacing:0.08em;text-transform:uppercase;}}
#ai-close{{background:none;border:none;color:#8b949e;cursor:pointer;font-size:16px;padding:0 4px;}}
#ai-body{{padding:14px;overflow-y:auto;flex:1;font-size:12px;color:#c9d1d9;line-height:1.75;}}
.otag{{background:#1f6feb22;border:1px solid #1f6feb44;border-radius:4px;
  padding:3px 9px;font-size:10px;color:#58a6ff;margin-bottom:10px;display:inline-block;}}
.ap{{margin-bottom:9px;}}
.err{{color:#ff6b6b;}}
.loading{{display:flex;align-items:center;gap:8px;color:#8b949e;}}
.dot{{animation:blink 1.2s infinite;font-size:14px;}}
.dot:nth-child(2){{animation-delay:.2s;}}.dot:nth-child(3){{animation-delay:.4s;}}
@keyframes blink{{0%,80%,100%{{opacity:0;}}40%{{opacity:1;}}}}
</style></head><body>
<div id="hud">
  🖱 Left-drag · Orbit &nbsp;|&nbsp; Right-drag · Pan &nbsp;|&nbsp; Scroll · Zoom<br>
  Click · Select &nbsp;|&nbsp; Drag arrows · Transform &nbsp;|&nbsp; <b>X</b> · AI Analyze<br>
  Mode: <span id="modeLabel">{mode}</span> &nbsp;|&nbsp; Snap: <span id="snapLabel">{"ON" if snap_on else "OFF"}</span>
</div>
<div id="status">Ready — add shapes from the sidebar</div>
<div id="dims"></div>
<button id="analyze-btn" onclick="triggerAnalyze()">🔍 Analyze (X)</button>
<div id="ai-panel">
  <div id="ai-hdr"><span>🤖 AI Analysis</span><button id="ai-close" onclick="closeAI()">✕</button></div>
  <div id="ai-body"><div class="loading"><span>Loading</span><span class="dot">●</span><span class="dot">●</span><span class="dot">●</span></div></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ── Config from Python
let transformMode = '{mode_js}';
let snapEnabled   = {snap_js};
let gridSize      = {grid_js};
let wireframeMode = {wire_js};

// ── Renderer
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setPixelRatio(devicePixelRatio);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);
function resize(){{renderer.setSize(innerWidth,innerHeight);cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix();}}
window.addEventListener('resize',resize);

// ── Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0d1117);
scene.fog = new THREE.FogExp2(0x0d1117, 0.012);

// ── Camera
const cam = new THREE.PerspectiveCamera(55,innerWidth/innerHeight,0.1,300);
const orb = {{theta:0.6,phi:1.1,r:16,tx:0,ty:0,tz:0}};
function applyCam(){{
  cam.position.set(
    orb.tx+orb.r*Math.sin(orb.phi)*Math.sin(orb.theta),
    orb.ty+orb.r*Math.cos(orb.phi),
    orb.tz+orb.r*Math.sin(orb.phi)*Math.cos(orb.theta));
  cam.lookAt(orb.tx,orb.ty,orb.tz);
}}

// ── Lights
scene.add(new THREE.AmbientLight(0x334466,0.9));
const sun=new THREE.DirectionalLight(0xffffff,1.4);
sun.position.set(10,18,8);sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-25;sun.shadow.camera.right=25;
sun.shadow.camera.top=25;sun.shadow.camera.bottom=-25;
scene.add(sun);
const fill=new THREE.DirectionalLight(0x4488ff,0.4);fill.position.set(-8,4,-6);scene.add(fill);

// ── Grid
const grid=new THREE.GridHelper(40,40,0x30363d,0x1a1f27);scene.add(grid);
const gnd=new THREE.Mesh(new THREE.PlaneGeometry(100,100),new THREE.MeshBasicMaterial({{visible:false,side:THREE.DoubleSide}}));
gnd.rotation.x=-Math.PI/2;gnd.name='_ground';scene.add(gnd);

// ── Dimension lines group
const dimGroup=new THREE.Group();dimGroup.name='_dims';scene.add(dimGroup);

// ── State
let objects=[],selected=null,colorIdx=0;
const COLORS=[0x4a9eff,0xff6b6b,0x6bffb8,0xffd93d,0xa78bfa,0xfb923c,0x34d399,0xf472b6,0xf9a8d4,0x93c5fd];
const nameCnt={{}};

function snap(v){{return snapEnabled?Math.round(v/gridSize)*gridSize:v;}}

// ── Gizmo
let gizmoGroup=null;
const AX={{x:0xff3333,y:0x33ff33,z:0x3388ff}};
function buildGizmo(){{
  if(gizmoGroup)scene.remove(gizmoGroup);
  gizmoGroup=new THREE.Group();gizmoGroup.name='_gizmo';
  ['x','y','z'].forEach(ax=>{{
    const g=new THREE.Group();g.userData.axis=ax;
    const shaft=new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.05,1.6,8),new THREE.MeshBasicMaterial({{color:AX[ax],depthTest:false}}));
    const tip=new THREE.Mesh(new THREE.ConeGeometry(0.13,0.4,8),new THREE.MeshBasicMaterial({{color:AX[ax],depthTest:false}}));
    tip.position.y=1.0;g.add(shaft,tip);g.userData.axis=ax;
    if(ax==='x'){{g.rotation.z=-Math.PI/2;g.position.x=1.0;}}
    if(ax==='y') g.position.y=1.0;
    if(ax==='z'){{g.rotation.x=Math.PI/2;g.position.z=1.0;}}
    gizmoGroup.add(g);
  }});
  scene.add(gizmoGroup);
}}
function syncGizmo(){{
  if(!selected||!gizmoGroup)return;
  gizmoGroup.position.copy(selected.position);
  gizmoGroup.scale.setScalar(Math.max(...selected.scale.toArray())*0.5+0.6);
}}

// ── Dimension display
function showDims(obj){{
  dimGroup.children.forEach(c=>dimGroup.remove(c));
  if(!obj){{document.getElementById('dims').style.display='none';return;}}
  const bb=new THREE.Box3().setFromObject(obj);
  const sz=new THREE.Vector3();bb.getSize(sz);
  const el=document.getElementById('dims');
  el.style.display='block';
  el.innerHTML=`<b>${{obj.userData.name}}</b><br>
    W: ${{sz.x.toFixed(3)}} &nbsp; H: ${{sz.y.toFixed(3)}} &nbsp; D: ${{sz.z.toFixed(3)}}<br>
    X: ${{obj.position.x.toFixed(3)}} &nbsp; Y: ${{obj.position.y.toFixed(3)}} &nbsp; Z: ${{obj.position.z.toFixed(3)}}`;
}}

// ── Shape definitions
function makeGeo(type){{
  switch(type){{
    case 'box':       return new THREE.BoxGeometry(1.5,1.5,1.5);
    case 'sphere':    return new THREE.SphereGeometry(0.85,32,32);
    case 'cylinder':  return new THREE.CylinderGeometry(0.7,0.7,1.8,32);
    case 'cone':      return new THREE.ConeGeometry(0.8,1.8,32);
    case 'torus':     return new THREE.TorusGeometry(0.7,0.25,16,64);
    case 'wedge':{{
      const g=new THREE.BufferGeometry();
      const v=new Float32Array([
        -0.75,0,-0.75, 0.75,0,-0.75, 0.75,0,0.75,
        -0.75,0,0.75,  -0.75,1.5,0.75, 0.75,1.5,0.75,
      ]);
      const i=[0,1,2,0,2,3,0,3,4,3,4,5,1,2,5,1,5,4,0,1,4,0,4,1,2,3,5];
      // simplified wedge via ExtrudeGeometry
      const shape=new THREE.Shape();
      shape.moveTo(-0.75,0);shape.lineTo(0.75,0);shape.lineTo(0.75,1.5);shape.lineTo(-0.75,0);
      return new THREE.ExtrudeGeometry(shape,{{depth:1.5,bevelEnabled:false}});
    }}
    case 'pipe':      return new THREE.TorusGeometry(0.6,0.15,12,48);
    case 'pyramid':{{
      const shape=new THREE.Shape();
      shape.moveTo(-0.75,-0.75);shape.lineTo(0.75,-0.75);
      shape.lineTo(0.75,0.75);shape.lineTo(-0.75,0.75);shape.closePath();
      const extrudeSettings={{depth:0.01,bevelEnabled:false}};
      // Use ConeGeometry with 4 segments as pyramid
      return new THREE.ConeGeometry(1.0,1.8,4);
    }}
    default: return new THREE.BoxGeometry(1.5,1.5,1.5);
  }}
}}

function addShape(type){{
  nameCnt[type]=(nameCnt[type]||0)+1;
  const mat=new THREE.MeshStandardMaterial({{
    color:COLORS[colorIdx++%COLORS.length],
    roughness:0.35,metalness:0.2,
    wireframe:wireframeMode
  }});
  const mesh=new THREE.Mesh(makeGeo(type),mat);
  mesh.castShadow=true;mesh.receiveShadow=true;
  const a=Math.random()*Math.PI*2,r=Math.random()*4;
  mesh.position.set(snap(Math.cos(a)*r),0.9,snap(Math.sin(a)*r));
  mesh.userData={{type,name:type+'_'+nameCnt[type]}};
  scene.add(mesh);objects.push(mesh);
  selectObj(mesh);
  setStatus('Added '+mesh.userData.name+' — X to analyze');
}}

// ── CAD Operations
function cadOp(op){{
  if(!selected&&op!=='clear')return setStatus('Select an object first');
  switch(op){{
    case 'union':
      if(objects.length<2)return setStatus('Need at least 2 objects for union (visual merge)');
      // Visual union: merge into group bounding box representation
      const others=objects.filter(o=>o!==selected);
      const target=others[others.length-1];
      // Move selected to overlap target, tint same color
      selected.position.copy(target.position);
      selected.material.color.copy(target.material.color);
      setStatus('Union: objects merged at same position');
      break;
    case 'subtract':
      // Visual subtract: make selected semi-transparent (hole effect)
      selected.material.transparent=true;
      selected.material.opacity=0.18;
      selected.material.wireframe=true;
      setStatus('Subtract: object shown as cutout (visual)');
      break;
    case 'extrude':
      selected.scale.y*=2.0;
      setStatus('Extruded '+selected.userData.name+' (Y scale ×2)');
      break;
    case 'duplicate':
      const mat2=selected.material.clone();
      const mesh2=new THREE.Mesh(selected.geometry,mat2);
      mesh2.position.set(selected.position.x+2,selected.position.y,selected.position.z);
      mesh2.rotation.copy(selected.rotation);
      mesh2.scale.copy(selected.scale);
      const baseName=selected.userData.name.replace(/_[0-9]+$/,'');
      nameCnt[baseName]=(nameCnt[baseName]||1)+1;
      mesh2.userData={{type:selected.userData.type,name:baseName+'_'+nameCnt[baseName]}};
      mesh2.castShadow=true;mesh2.receiveShadow=true;
      scene.add(mesh2);objects.push(mesh2);
      selectObj(mesh2);
      setStatus('Duplicated → '+mesh2.userData.name);
      break;
    case 'mirrorX':
      selected.scale.x*=-1;
      setStatus('Mirrored '+selected.userData.name+' on X axis');
      break;
    case 'mirrorY':
      selected.scale.z*=-1;
      setStatus('Mirrored '+selected.userData.name+' on Z axis');
      break;
  }}
  syncGizmo();showDims(selected);
}}

// ── Select / Deselect
function selectObj(obj){{
  if(selected&&selected!==obj)selected.material.emissive.setHex(0x000000);
  selected=obj;
  const btn=document.getElementById('analyze-btn');
  if(selected){{
    selected.material.emissive.setHex(0x112244);
    buildGizmo();syncGizmo();showDims(selected);
    setStatus('✓ '+selected.userData.name+' — X to analyze with AI');
    btn.style.display='block';
  }}else{{
    if(gizmoGroup){{scene.remove(gizmoGroup);gizmoGroup=null;}}
    showDims(null);btn.style.display='none';setStatus('Ready');
  }}
}}

function deleteSelected(){{
  if(!selected)return;
  scene.remove(selected);objects=objects.filter(o=>o!==selected);
  if(gizmoGroup){{scene.remove(gizmoGroup);gizmoGroup=null;}}
  selected=null;showDims(null);
  document.getElementById('analyze-btn').style.display='none';
  closeAI();setStatus('Deleted');
}}

function clearScene(){{
  objects.forEach(o=>scene.remove(o));objects=[];colorIdx=0;
  Object.keys(nameCnt).forEach(k=>delete nameCnt[k]);
  if(gizmoGroup){{scene.remove(gizmoGroup);gizmoGroup=null;}}
  selected=null;showDims(null);closeAI();
  document.getElementById('analyze-btn').style.display='none';
  setStatus('Scene cleared');
}}

function setColor(hex){{
  if(!selected)return setStatus('Select an object first');
  selected.material.color.set(hex);
  selected.material.wireframe=wireframeMode;
  setStatus('Color applied to '+selected.userData.name);
}}

function applyPos(x,y,z){{
  if(!selected)return;
  selected.position.set(parseFloat(x),parseFloat(y),parseFloat(z));
  syncGizmo();showDims(selected);
  setStatus('Position set to ('+x+', '+y+', '+z+')');
}}

function applyScale(x,y,z){{
  if(!selected)return;
  selected.scale.set(parseFloat(x),parseFloat(y),parseFloat(z));
  syncGizmo();showDims(selected);
  setStatus('Scale set to ('+x+', '+y+', '+z+')');
}}

// ── AI trigger (posts to Streamlit via URL → server handles it)
function closeAI(){{document.getElementById('ai-panel').style.display='none';}}

function triggerAnalyze(){{
  if(!selected)return setStatus('Select an object first');
  const panel=document.getElementById('ai-panel');
  const body=document.getElementById('ai-body');
  panel.style.display='flex';
  body.innerHTML='<div class="loading"><span>Analyzing</span><span class="dot">●</span><span class="dot">●</span><span class="dot">●</span></div>';
  setStatus('Sending to AI...');

  const c=selected.material.color;
  const obj={{
    name:selected.userData.name,type:selected.userData.type,
    position:selected.position.toArray().map(v=>+v.toFixed(3)),
    rotation:[selected.rotation.x,selected.rotation.y,selected.rotation.z].map(v=>+v.toFixed(3)),
    scale:selected.scale.toArray().map(v=>+v.toFixed(3)),
    color:'#'+c.getHexString(),total:objects.length
  }};
  const encoded=encodeURIComponent(JSON.stringify(obj));
  const url=new URL(window.parent.location.href);
  url.searchParams.set('analyze',encoded);
  window.parent.location.href=url.toString();
}}

// ── Show AI result if Python already computed it
(function(){{
  const result={ai_result_js};
  const objStr={ai_obj_js};
  if(!result||!objStr)return;
  const panel=document.getElementById('ai-panel');
  const body=document.getElementById('ai-body');
  panel.style.display='flex';
  try{{
    const obj=JSON.parse(objStr);
    if(result.startsWith('ERROR:')){{
      body.innerHTML='<div class="otag">'+obj.name+'</div><div class="err">❌ '+result.replace('ERROR:','')+'</div>';
    }}else{{
      const paras=result.split('\n').filter(l=>l.trim()).map(l=>'<div class="ap">'+l+'</div>').join('');
      body.innerHTML='<div class="otag">'+obj.name+' · '+obj.type+'</div>'+paras;
    }}
  }}catch(e){{body.innerHTML='<div class="ap">'+result+'</div>';}}
}})();

// ── Keyboard
document.addEventListener('keydown',e=>{{
  const t=document.activeElement.tagName;
  if(t==='INPUT'||t==='TEXTAREA')return;
  if(e.key.toLowerCase()==='x')triggerAnalyze();
  if(e.key==='Escape')closeAI();
  if(e.key==='Delete')deleteSelected();
}});

// ── Raycaster
const ray=new THREE.Raycaster(),mp=new THREE.Vector2();
function getHits(ev,targets){{
  const rc=renderer.domElement.getBoundingClientRect();
  mp.x=((ev.clientX-rc.left)/rc.width)*2-1;
  mp.y=-((ev.clientY-rc.top)/rc.height)*2+1;
  ray.setFromCamera(mp,cam);
  return ray.intersectObjects(targets,true);
}}

// ── Mouse
let isOrb=false,isPan=false,isDrag=false;
let lm={{x:0,y:0}},dm={{x:0,y:0}},dragAxis=null,sp=null,sr=null,ss=null;

renderer.domElement.addEventListener('mousedown',e=>{{
  dm={{x:e.clientX,y:e.clientY}};
  if(selected&&gizmoGroup){{
    const all=[];gizmoGroup.traverse(c=>{{if(c.isMesh)all.push(c);}});
    const hits=getHits(e,all);
    if(hits.length){{
      let a=hits[0].object;
      while(a.parent&&!a.userData.axis)a=a.parent;
      dragAxis=a.userData.axis;isDrag=true;
      sp=selected.position.clone();sr=selected.rotation.clone();ss=selected.scale.clone();
      lm={{x:e.clientX,y:e.clientY}};return;
    }}
  }}
  if(e.button===0)isOrb=true;
  if(e.button===2)isPan=true;
  lm={{x:e.clientX,y:e.clientY}};
}});

renderer.domElement.addEventListener('mouseup',e=>{{
  if(isDrag){{isDrag=false;dragAxis=null;showDims(selected);return;}}
  isOrb=false;isPan=false;
  if(Math.abs(e.clientX-dm.x)<5&&Math.abs(e.clientY-dm.y)<5&&e.button===0){{
    const hits=getHits(e,objects);
    selectObj(hits.length?hits[0].object:null);
  }}
}});

renderer.domElement.addEventListener('mousemove',e=>{{
  if(isDrag&&selected&&dragAxis){{
    const dx=(e.clientX-lm.x)*0.02,dy=-(e.clientY-lm.y)*0.02;
    const d=Math.abs(dx)>Math.abs(dy)?dx:dy;
    if(transformMode==='move'){{
      const p=sp.clone();
      if(dragAxis==='x')p.x=snap(sp.x+dx*2.5);
      if(dragAxis==='y')p.y=snap(sp.y+dy*2.5);
      if(dragAxis==='z')p.z=snap(sp.z+dx*2.5);
      selected.position.copy(p);
    }}else if(transformMode==='rotate'){{
      const r=sr.clone();
      if(dragAxis==='x')r.x+=d*3;
      if(dragAxis==='y')r.y+=d*3;
      if(dragAxis==='z')r.z+=d*3;
      selected.rotation.copy(r);
    }}else if(transformMode==='scale'){{
      const sc=ss.clone(),f=1+d*1.5;
      if(dragAxis==='x')sc.x=Math.max(0.05,ss.x*f);
      if(dragAxis==='y')sc.y=Math.max(0.05,ss.y*f);
      if(dragAxis==='z')sc.z=Math.max(0.05,ss.z*f);
      selected.scale.copy(sc);
    }}
    syncGizmo();lm={{x:e.clientX,y:e.clientY}};return;
  }}
  if(isOrb){{
    orb.theta-=(e.clientX-lm.x)*0.007;
    orb.phi-=(e.clientY-lm.y)*0.007;
    orb.phi=Math.max(0.08,Math.min(Math.PI-0.08,orb.phi));
  }}
  if(isPan){{
    const spd=0.012*(orb.r/10);
    const right=new THREE.Vector3().crossVectors(
      new THREE.Vector3(Math.sin(orb.phi)*Math.sin(orb.theta),Math.cos(orb.phi),Math.sin(orb.phi)*Math.cos(orb.theta)),
      new THREE.Vector3(0,1,0)).normalize();
    orb.tx-=right.x*(e.clientX-lm.x)*spd;
    orb.tz-=right.z*(e.clientX-lm.x)*spd;
    orb.ty+=(e.clientY-lm.y)*spd;
  }}
  lm={{x:e.clientX,y:e.clientY}};
}});
renderer.domElement.addEventListener('wheel',e=>{{
  orb.r*=1+e.deltaY*0.001;orb.r=Math.max(2,Math.min(80,orb.r));
}},{{passive:true}});
renderer.domElement.addEventListener('contextmenu',e=>e.preventDefault());

function setStatus(msg){{document.getElementById('status').innerText=msg;}}

// ── Handle sidebar commands
(function(){{
  const cmd={js_cmd};
  if(!cmd||cmd==='null')return;
  if(cmd.startsWith('add:')){{addShape(cmd.split(':')[1]);return;}}
  if(cmd.startsWith('cad:')){{cadOp(cmd.split(':')[1]);return;}}
  if(cmd==='delete'){{deleteSelected();return;}}
  if(cmd==='clear'){{clearScene();return;}}
  if(cmd.startsWith('color:')){{setColor(cmd.split(':')[1]);return;}}
  if(cmd.startsWith('pos:')){{const v=cmd.slice(4).split(',');applyPos(v[0],v[1],v[2]);return;}}
  if(cmd.startsWith('scale:')){{const v=cmd.slice(6).split(',');applyScale(v[0],v[1],v[2]);return;}}
}})();

// ── Render loop
(function animate(){{
  requestAnimationFrame(animate);
  applyCam();
  if(selected&&gizmoGroup)syncGizmo();
  renderer.render(scene,cam);
}})();
resize();
</script></body></html>"""

st.markdown("## 🔩 CAD AI Studio")
components.html(HTML, height=700, scrolling=False)
st.caption("Click shape to select · Drag colored arrows to transform · **X** to AI analyze · Snap keeps positions aligned to grid")