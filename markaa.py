import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AI 3D Studio", layout="wide", page_icon="🧊")

st.markdown("""
<style>
body, .stApp { background:#0d1117 !important; color:#e6edf3; }
[data-testid="stSidebar"] { background:#161b22 !important; border-right:1px solid #30363d; }
[data-testid="stSidebar"] * { color:#c9d1d9 !important; }
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

    st.markdown("### 🔑 AI API Key")
    api_key = st.text_input(
        "Paste your API key",
        type="password",
        placeholder="sk-... or AIza... or gsk_...",
        label_visibility="collapsed"
    )
    if api_key:
        if api_key.startswith("sk-ant"):
            provider = "anthropic"
            st.success("✓ Anthropic key detected")
        elif api_key.startswith("sk-") and not api_key.startswith("sk-ant"):
            provider = "openai"
            st.success("✓ OpenAI key detected")
        elif api_key.startswith("AIza"):
            provider = "gemini"
            st.success("✓ Google Gemini key detected")
        elif api_key.startswith("gsk_"):
            provider = "groq"
            st.success("✓ Groq key detected")
        else:
            provider = "openai"
            st.info("ℹ Key format unknown — will try OpenAI-compatible")
    else:
        provider = "none"
        st.caption("Enter your API key to enable AI analysis")

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
    st.markdown("### 🗑 Scene")
    delete_sel = st.button("🗑 Delete Selected")
    clear_all  = st.button("✕ Clear All")

    st.markdown("---")
    st.markdown("### 🎨 Color")
    color_pick  = st.color_picker("Color", "#4a9eff")
    apply_color = st.button("Apply Color")

    st.markdown("---")
    st.markdown("### 🤖 Analysis Mode")
    analysis_mode = st.selectbox("", [
        "General Design Review",
        "Structural Analysis",
        "Aesthetic & Composition",
        "Optimization Suggestions",
        "Architecture Critique",
    ], label_visibility="collapsed")

    if api_key:
        st.markdown("""
        <div style='background:#1f6feb22;border:1px solid #1f6feb55;border-radius:6px;
        padding:10px 12px;font-size:12px;color:#58a6ff;margin-top:8px;'>
        Click an object to select it, then click <b>Select & Analyze</b> or press <b>X</b>.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#ff6b6b22;border:1px solid #ff6b6b55;border-radius:6px;
        padding:10px 12px;font-size:12px;color:#ff6b6b;margin-top:8px;'>
        ⚠ Enter API key above to enable AI analysis.
        </div>
        """, unsafe_allow_html=True)

# ── JS command from sidebar buttons ──────────────────────────
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

# ── Viewport ──────────────────────────────────────────────────
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
  padding:8px 13px; font-size:10px; color:#8b949e; line-height:2; pointer-events:none;
}}
#status {{
  position:absolute; bottom:60px; left:10px; right:10px; text-align:center;
  background:#161b2299; border:1px solid #30363d; border-radius:6px;
  padding:5px 14px; font-size:11px; color:#c9d1d9; pointer-events:none;
}}
#analyze-btn {{
  position:absolute; bottom:10px; left:50%; transform:translateX(-50%);
  background:#1f6feb; color:#fff; border:none; border-radius:6px;
  padding:9px 28px; font-size:13px; font-family:monospace; cursor:pointer;
  transition:all 0.15s; display:none; letter-spacing:0.04em;
}}
#analyze-btn:hover {{ background:#388bfd; }}
#analyze-btn:disabled {{ background:#21262d; color:#484f58; cursor:default; }}

/* AI Result Panel */
#ai-panel {{
  position:absolute; top:10px; right:10px; width:320px;
  background:#161b22f0; border:1px solid #30363d; border-radius:8px;
  display:none; flex-direction:column;
  max-height:calc(100% - 80px); box-shadow:0 8px 32px #00000088;
}}
#ai-header {{
  display:flex; align-items:center; justify-content:space-between;
  padding:10px 14px; border-bottom:1px solid #30363d; flex-shrink:0;
}}
#ai-header-title {{ color:#58a6ff; font-size:11px; letter-spacing:0.08em; text-transform:uppercase; }}
#ai-close {{
  background:none; border:none; color:#8b949e;
  cursor:pointer; font-size:16px; padding:0 4px;
}}
#ai-close:hover {{ color:#e6edf3; }}
#ai-body {{
  padding:14px; overflow-y:auto; flex:1;
  font-size:12px; color:#c9d1d9; line-height:1.75;
}}
.obj-tag {{
  background:#1f6feb22; border:1px solid #1f6feb44; border-radius:4px;
  padding:3px 9px; font-size:10px; color:#58a6ff;
  margin-bottom:12px; display:inline-block;
}}
.loading {{ display:flex; align-items:center; gap:8px; color:#8b949e; }}
.dot {{ animation:blink 1.2s infinite; font-size:16px; }}
.dot:nth-child(2){{ animation-delay:0.2s; }}
.dot:nth-child(3){{ animation-delay:0.4s; }}
@keyframes blink {{ 0%,80%,100%{{opacity:0;}} 40%{{opacity:1;}} }}
.ai-para {{ margin-bottom:10px; }}
.error-msg {{ color:#ff6b6b; font-size:12px; }}
</style>
</head>
<body>
<div id="hud">
  🖱 Left-drag · Orbit &nbsp;|&nbsp; Right-drag · Pan &nbsp;|&nbsp; Scroll · Zoom<br>
  Click object · Select &nbsp;|&nbsp; Drag colored arrows · Transform<br>
  <b>Select & Analyze</b> button or <b>X key</b> · Run AI
</div>
<div id="status">Ready — add shapes from the sidebar</div>
<button id="analyze-btn" onclick="analyzeSelected()">🔍 Select &amp; Analyze</button>

<div id="ai-panel">
  <div id="ai-header">
    <span id="ai-header-title">🤖 AI Analysis</span>
    <button id="ai-close" onclick="closePanel()">✕</button>
  </div>
  <div id="ai-body"></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ── Config injected from Python ───────────────────────────────
const API_KEY       = "{api_key}";
const PROVIDER      = "{provider}";
const ANALYSIS_MODE = "{analysis_mode}";

// ── Renderer ──────────────────────────────────────────────────
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setPixelRatio(devicePixelRatio);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);
function resize() {{
  renderer.setSize(innerWidth, innerHeight);
  cam.aspect = innerWidth/innerHeight;
  cam.updateProjectionMatrix();
}}
window.addEventListener('resize', resize);

// ── Scene + Camera ────────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0d1117);
scene.fog = new THREE.FogExp2(0x0d1117, 0.015);

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
const sun = new THREE.DirectionalLight(0xffffff,1.4);
sun.position.set(10,18,8); sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
['left','right','top','bottom'].forEach((s,i)=>sun.shadow.camera[s]=[-20,20,20,-20][i]);
scene.add(sun);
scene.add(Object.assign(new THREE.DirectionalLight(0x4488ff,0.4),{{position:{{set:()=>{{}}}}}}));
const fill = new THREE.DirectionalLight(0x4488ff,0.4); fill.position.set(-8,4,-6); scene.add(fill);

scene.add(new THREE.GridHelper(30,30,0x30363d,0x1a1f27));
const gnd = new THREE.Mesh(new THREE.PlaneGeometry(100,100),new THREE.MeshBasicMaterial({{visible:false,side:THREE.DoubleSide}}));
gnd.rotation.x=-Math.PI/2; gnd.name='_ground'; scene.add(gnd);

// ── State ─────────────────────────────────────────────────────
let objects=[], selected=null, transformMode='{mode_js}', colorIdx=0;
const COLORS=[0x4a9eff,0xff6b6b,0x6bffb8,0xffd93d,0xa78bfa,0xfb923c,0x34d399,0xf472b6];
const nameCnt={{}};

// ── Gizmo ─────────────────────────────────────────────────────
let gizmoGroup=null;
const AX={{x:0xff4444,y:0x44ff44,z:0x4488ff}};
function buildGizmo() {{
  if(gizmoGroup) scene.remove(gizmoGroup);
  gizmoGroup=new THREE.Group();
  ['x','y','z'].forEach(ax=>{{
    const g=new THREE.Group(); g.userData.axis=ax;
    g.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.05,1.5,8),new THREE.MeshBasicMaterial({{color:AX[ax],depthTest:false}}))));
    const tip=new THREE.Mesh(new THREE.ConeGeometry(0.13,0.38,8),new THREE.MeshBasicMaterial({{color:AX[ax],depthTest:false}}));
    tip.position.y=0.94; g.add(tip);
    if(ax==='x'){{g.rotation.z=-Math.PI/2;g.position.x=0.95;}}
    if(ax==='y') g.position.y=0.95;
    if(ax==='z'){{g.rotation.x=Math.PI/2;g.position.z=0.95;}}
    gizmoGroup.add(g);
  }});
  scene.add(gizmoGroup);
}}
function syncGizmo() {{
  if(!selected||!gizmoGroup) return;
  gizmoGroup.position.copy(selected.position);
  gizmoGroup.scale.setScalar(Math.max(...selected.scale.toArray())*0.55+0.5);
}}

// ── Shapes ────────────────────────────────────────────────────
const GEOS={{
  cube:()=>new THREE.BoxGeometry(1.2,1.2,1.2),
  sphere:()=>new THREE.SphereGeometry(0.75,32,32),
  cylinder:()=>new THREE.CylinderGeometry(0.6,0.6,1.5,32),
  cone:()=>new THREE.ConeGeometry(0.7,1.5,32),
  torus:()=>new THREE.TorusGeometry(0.65,0.22,16,64),
  plane:()=>new THREE.PlaneGeometry(2,2),
}};
function addShape(type) {{
  nameCnt[type]=(nameCnt[type]||0)+1;
  const mat=new THREE.MeshStandardMaterial({{color:COLORS[colorIdx++%COLORS.length],roughness:0.38,metalness:0.18}});
  const mesh=new THREE.Mesh(GEOS[type](),mat);
  mesh.castShadow=true; mesh.receiveShadow=true;
  const a=Math.random()*Math.PI*2, r=Math.random()*3;
  mesh.position.set(Math.cos(a)*r,0.8,Math.sin(a)*r);
  mesh.userData={{type,name:type+'_'+nameCnt[type]}};
  scene.add(mesh); objects.push(mesh);
  selectObj(mesh);
  setStatus('Added '+mesh.userData.name);
}}

// ── Select ────────────────────────────────────────────────────
function selectObj(obj) {{
  if(selected&&selected!==obj) selected.material.emissive.setHex(0x000000);
  selected=obj;
  const btn=document.getElementById('analyze-btn');
  if(selected) {{
    selected.material.emissive.setHex(0x223355);
    buildGizmo(); syncGizmo();
    setStatus('Selected: '+selected.userData.name+(API_KEY?' — click Analyze or press X':'  (add API key to analyze)'));
    btn.style.display = API_KEY ? 'block' : 'none';
  }} else {{
    if(gizmoGroup){{scene.remove(gizmoGroup);gizmoGroup=null;}}
    btn.style.display='none';
    setStatus('Ready');
  }}
}}

function deleteSelected() {{
  if(!selected) return;
  scene.remove(selected); objects=objects.filter(o=>o!==selected);
  if(gizmoGroup){{scene.remove(gizmoGroup);gizmoGroup=null;}}
  selected=null; closePanel();
  document.getElementById('analyze-btn').style.display='none';
  setStatus('Deleted');
}}

function clearScene() {{
  objects.forEach(o=>scene.remove(o)); objects=[]; colorIdx=0;
  Object.keys(nameCnt).forEach(k=>delete nameCnt[k]);
  if(gizmoGroup){{scene.remove(gizmoGroup);gizmoGroup=null;}}
  selected=null; closePanel();
  document.getElementById('analyze-btn').style.display='none';
  setStatus('Scene cleared');
}}

function setColor(hex) {{
  if(selected) {{ selected.material.color.set(hex); setStatus('Color applied'); }}
}}

// ── AI Analysis ───────────────────────────────────────────────
function closePanel() {{
  document.getElementById('ai-panel').style.display='none';
}}

function buildPrompt(obj) {{
  const modes = {{
    "General Design Review":    "Give a concise design review: placement, scale, and role in the scene.",
    "Structural Analysis":      "Analyze structural placement and spatial logic.",
    "Aesthetic & Composition":  "Evaluate color, scale, and visual contribution.",
    "Optimization Suggestions": "Give specific improvements for position, scale, color, or shape.",
    "Architecture Critique":    "Critique as an architect: proportions, placement, form.",
  }};
  return `You are an expert 3D designer. Analyze this selected 3D object:
Name: ${{obj.name}}
Type: ${{obj.type}}
Position: ${{JSON.stringify(obj.position)}}
Rotation (radians): ${{JSON.stringify(obj.rotation)}}
Scale: ${{JSON.stringify(obj.scale)}}
Color: ${{obj.color}}
Total objects in scene: ${{obj.total}}

Task: ${{modes[ANALYSIS_MODE] || modes["General Design Review"]}}

Be concise and specific. 3-5 short paragraphs. Reference actual values.`;
}}

async function callAI(prompt) {{
  // OpenAI & Groq share the same API shape; Anthropic and Gemini differ
  if(PROVIDER === 'openai' || PROVIDER === 'groq') {{
    const url = PROVIDER==='groq'
      ? 'https://api.groq.com/openai/v1/chat/completions'
      : 'https://api.openai.com/v1/chat/completions';
    const model = PROVIDER==='groq' ? 'llama3-8b-8192' : 'gpt-4o-mini';
    const r = await fetch(url, {{
      method:'POST',
      headers:{{'Authorization':'Bearer '+API_KEY,'Content-Type':'application/json'}},
      body: JSON.stringify({{model, max_tokens:500, messages:[{{role:'user',content:prompt}}]}})
    }});
    const d = await r.json();
    if(!r.ok) throw new Error(d.error?.message || r.statusText);
    return d.choices[0].message.content;

  }} else if(PROVIDER === 'anthropic') {{
    const r = await fetch('https://api.anthropic.com/v1/messages', {{
      method:'POST',
      headers:{{'x-api-key':API_KEY,'anthropic-version':'2023-06-01','content-type':'application/json'}},
      body: JSON.stringify({{model:'claude-haiku-4-5-20251001',max_tokens:500,messages:[{{role:'user',content:prompt}}]}})
    }});
    const d = await r.json();
    if(!r.ok) throw new Error(d.error?.message || r.statusText);
    return d.content[0].text;

  }} else if(PROVIDER === 'gemini') {{
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${{API_KEY}}`;
    const r = await fetch(url, {{
      method:'POST',
      headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify({{contents:[{{parts:[{{text:prompt}}]}}]}})
    }});
    const d = await r.json();
    if(!r.ok) throw new Error(d.error?.message || r.statusText);
    return d.candidates[0].content.parts[0].text;
  }}

  throw new Error('Unknown provider: '+PROVIDER);
}}

async function analyzeSelected() {{
  if(!selected) return setStatus('Click an object first');
  if(!API_KEY)  return setStatus('No API key — enter one in the sidebar');

  const panel=document.getElementById('ai-panel');
  const body=document.getElementById('ai-body');
  panel.style.display='flex';
  body.innerHTML=`<div class="obj-tag">${{selected.userData.name}} · ${{selected.userData.type}}</div>
    <div class="loading"><span>Analyzing</span>
    <span class="dot">●</span><span class="dot">●</span><span class="dot">●</span></div>`;

  setStatus('Sending to AI...');

  const c=selected.material.color;
  const obj={{
    name:  selected.userData.name,
    type:  selected.userData.type,
    position: selected.position.toArray().map(v=>+v.toFixed(3)),
    rotation: [selected.rotation.x,selected.rotation.y,selected.rotation.z].map(v=>+v.toFixed(3)),
    scale: selected.scale.toArray().map(v=>+v.toFixed(3)),
    color: '#'+c.getHexString(),
    total: objects.length,
  }};

  try {{
    const text = await callAI(buildPrompt(obj));
    const html = text.split('\n').filter(l=>l.trim())
      .map(l=>`<div class="ai-para">${{l}}</div>`).join('');
    body.innerHTML=`<div class="obj-tag">${{obj.name}} · ${{obj.type}} · ${{obj.color}}</div>${{html}}`;
    setStatus('Analysis done — press X or click Analyze anytime');
  }} catch(err) {{
    body.innerHTML=`<div class="obj-tag">${{obj.name}}</div>
      <div class="error-msg">❌ ${{err.message}}<br><br>
      Check your API key and provider in the sidebar.</div>`;
    setStatus('AI error — see panel');
  }}
}}

// ── X key shortcut ────────────────────────────────────────────
document.addEventListener('keydown', e=>{{
  const tag=document.activeElement.tagName;
  if(tag==='INPUT'||tag==='TEXTAREA') return;
  if(e.key.toLowerCase()==='x') analyzeSelected();
  if(e.key==='Escape') closePanel();
  if(e.key==='Delete'||e.key==='Backspace') deleteSelected();
}});

// ── Raycaster ─────────────────────────────────────────────────
const ray=new THREE.Raycaster(), mp=new THREE.Vector2();
function getHits(ev,targets) {{
  const rc=renderer.domElement.getBoundingClientRect();
  mp.x=((ev.clientX-rc.left)/rc.width)*2-1;
  mp.y=-((ev.clientY-rc.top)/rc.height)*2+1;
  ray.setFromCamera(mp,cam);
  return ray.intersectObjects(targets,true);
}}

// ── Mouse ─────────────────────────────────────────────────────
let isOrb=false,isPan=false,isDrag=false;
let lm={{x:0,y:0}},dm={{x:0,y:0}};
let dragAxis=null,sp=null,sr=null,ss=null;

renderer.domElement.addEventListener('mousedown',e=>{{
  dm={{x:e.clientX,y:e.clientY}};
  if(selected&&gizmoGroup){{
    const all=[]; gizmoGroup.traverse(c=>{{if(c.isMesh)all.push(c);}});
    const hits=getHits(e,all);
    if(hits.length){{
      let a=hits[0].object;
      while(a.parent&&!a.userData.axis) a=a.parent;
      dragAxis=a.userData.axis; isDrag=true;
      sp=selected.position.clone(); sr=selected.rotation.clone(); ss=selected.scale.clone();
      lm={{x:e.clientX,y:e.clientY}}; return;
    }}
  }}
  if(e.button===0) isOrb=true;
  if(e.button===2) isPan=true;
  lm={{x:e.clientX,y:e.clientY}};
}});

renderer.domElement.addEventListener('mouseup',e=>{{
  if(isDrag){{isDrag=false;dragAxis=null;return;}}
  isOrb=false; isPan=false;
  if(Math.abs(e.clientX-dm.x)<5&&Math.abs(e.clientY-dm.y)<5&&e.button===0){{
    const hits=getHits(e,objects);
    selectObj(hits.length?hits[0].object:null);
  }}
}});

renderer.domElement.addEventListener('mousemove',e=>{{
  if(isDrag&&selected&&dragAxis){{
    const dx=(e.clientX-lm.x)*0.02, dy=-(e.clientY-lm.y)*0.02;
    const d=Math.abs(dx)>Math.abs(dy)?dx:dy;
    if(transformMode==='move'){{
      const p=sp.clone();
      if(dragAxis==='x') p.x+=dx*2.2;
      if(dragAxis==='y') p.y+=dy*2.2;
      if(dragAxis==='z') p.z+=dx*2.2;
      selected.position.copy(p);
    }} else if(transformMode==='rotate'){{
      const r=sr.clone();
      if(dragAxis==='x') r.x+=d*3;
      if(dragAxis==='y') r.y+=d*3;
      if(dragAxis==='z') r.z+=d*3;
      selected.rotation.copy(r);
    }} else if(transformMode==='scale'){{
      const sc=ss.clone(),f=1+d*1.5;
      if(dragAxis==='x') sc.x=Math.max(0.05,ss.x*f);
      if(dragAxis==='y') sc.y=Math.max(0.05,ss.y*f);
      if(dragAxis==='z') sc.z=Math.max(0.05,ss.z*f);
      selected.scale.copy(sc);
    }}
    syncGizmo(); lm={{x:e.clientX,y:e.clientY}}; return;
  }}
  if(isOrb){{
    orb.theta-=(e.clientX-lm.x)*0.007;
    orb.phi  -=(e.clientY-lm.y)*0.007;
    orb.phi=Math.max(0.08,Math.min(Math.PI-0.08,orb.phi));
  }}
  if(isPan){{
    const spd=0.012*(orb.r/10);
    const right=new THREE.Vector3().crossVectors(
      new THREE.Vector3(Math.sin(orb.phi)*Math.sin(orb.theta),Math.cos(orb.phi),Math.sin(orb.phi)*Math.cos(orb.theta)),
      new THREE.Vector3(0,1,0)
    ).normalize();
    orb.tx-=right.x*(e.clientX-lm.x)*spd;
    orb.tz-=right.z*(e.clientX-lm.x)*spd;
    orb.ty+=(e.clientY-lm.y)*spd;
  }}
  lm={{x:e.clientX,y:e.clientY}};
}});
renderer.domElement.addEventListener('wheel',e=>{{
  orb.r*=1+e.deltaY*0.001; orb.r=Math.max(2,Math.min(80,orb.r));
}},{{passive:true}});
renderer.domElement.addEventListener('contextmenu',e=>e.preventDefault());

function setStatus(msg){{document.getElementById('status').innerText=msg;}}

// ── Sidebar button commands ───────────────────────────────────
(function(){{
  const cmd={js_cmd};
  if(!cmd||cmd==='null') return;
  if(cmd.startsWith('addShape:')){{addShape(cmd.split(':')[1]);return;}}
  if(cmd==='deleteSelected'){{deleteSelected();return;}}
  if(cmd==='clearScene'){{clearScene();return;}}
  if(cmd.startsWith('setColor:')){{setColor(cmd.split(':')[1]);return;}}
}})();

// ── Render loop ───────────────────────────────────────────────
(function animate(){{
  requestAnimationFrame(animate);
  applyCam();
  if(selected&&gizmoGroup) syncGizmo();
  renderer.render(scene,cam);
}})();
resize();
</script>
</body>
</html>"""

st.markdown("## 🧊 AI 3D Studio")
components.html(HTML, height=700, scrolling=False)
st.caption("Add shapes → click to select → click **Select & Analyze** (or press **X**) → AI panel appears. Press Esc to close.")