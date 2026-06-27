import streamlit as st
import streamlit.components.v1 as components
import anthropic
import json

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
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] span, [data-testid="stSidebar"] div { color:#c9d1d9 !important; }
.stButton > button {
  background:#21262d; color:#c9d1d9; border:1px solid #30363d;
  border-radius:6px; font-size:13px; width:100%; margin:2px 0; transition:all 0.15s;
}
.stButton > button:hover { background:#1f6feb; border-color:#1f6feb; color:#fff; }
textarea, input { background:#0d1117 !important; color:#c9d1d9 !important; border:1px solid #30363d !important; }
.stSelectbox > div > div { background:#0d1117 !important; color:#c9d1d9 !important; border:1px solid #30363d !important; }
footer, header, #MainMenu { visibility:hidden; }
.block-container { padding-top:1rem; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧊 AI 3D Studio")
    st.markdown("---")

    st.markdown("### ➕ Add Shape")
    c1, c2 = st.columns(2)
    with c1:
        add_cube      = st.button("⬛ Cube")
        add_cylinder  = st.button("🔵 Cylinder")
        add_cone      = st.button("🔺 Cone")
    with c2:
        add_sphere    = st.button("⚪ Sphere")
        add_torus     = st.button("⭕ Torus")
        add_plane     = st.button("▭ Plane")

    st.markdown("---")
    st.markdown("### 🎮 Transform Mode")
    mode = st.radio("", ["Move", "Rotate", "Scale"], horizontal=True, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### 🗑️ Scene")
    delete_sel = st.button("🗑 Delete Selected")
    clear_all  = st.button("✕ Clear All")

    st.markdown("---")
    st.markdown("### 🎨 Object Color")
    color_pick  = st.color_picker("Pick color", "#4a9eff")
    apply_color = st.button("Apply Color to Selected")

    st.markdown("---")
    st.markdown("### 🤖 AI Analysis")
    analysis_mode = st.selectbox("Mode", [
        "General Design Review",
        "Structural Analysis",
        "Aesthetic & Composition",
        "Optimization Suggestions",
        "Architecture Critique",
    ])
    custom_q = st.text_area("Custom question", height=60,
                             placeholder="e.g. Does this look balanced?",
                             label_visibility="collapsed")
    analyze = st.button("🔍 Analyze with Claude")

# ── Determine JS command to inject this frame ─────────────────
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

# ── Three.js viewport ─────────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html>
<head>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#0d1117;overflow:hidden;font-family:monospace;user-select:none;}}
canvas{{display:block;}}
#hud{{
  position:absolute;top:8px;left:8px;
  background:#161b2299;border:1px solid #30363d;border-radius:6px;
  padding:7px 12px;font-size:10px;color:#8b949e;line-height:1.9;pointer-events:none;
}}
#status{{
  position:absolute;bottom:8px;left:8px;right:8px;text-align:center;
  background:#161b2299;border:1px solid #30363d;border-radius:6px;
  padding:5px 12px;font-size:11px;color:#c9d1d9;pointer-events:none;
}}
</style>
</head>
<body>
<div id="hud">
  🖱 Left-drag · Orbit &nbsp;|&nbsp; Right-drag · Pan &nbsp;|&nbsp; Scroll · Zoom<br>
  Click object · Select &nbsp;|&nbsp; Drag colored arrows · Transform<br>
  Mode: <b id="modeLabel">{mode}</b>
</div>
<div id="status">Ready — add a shape from the left sidebar</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ── Renderer
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setPixelRatio(devicePixelRatio);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

function resize(){{
  renderer.setSize(innerWidth, innerHeight);
  cam.aspect = innerWidth/innerHeight;
  cam.updateProjectionMatrix();
}}
window.addEventListener('resize', resize);

// ── Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0d1117);
scene.fog = new THREE.FogExp2(0x0d1117, 0.015);

// ── Camera
const cam = new THREE.PerspectiveCamera(55, innerWidth/innerHeight, 0.1, 300);
const orb = {{theta:0.6, phi:1.1, r:14, tx:0, ty:0, tz:0}};
function applyCam(){{
  cam.position.set(
    orb.tx + orb.r*Math.sin(orb.phi)*Math.sin(orb.theta),
    orb.ty + orb.r*Math.cos(orb.phi),
    orb.tz + orb.r*Math.sin(orb.phi)*Math.cos(orb.theta)
  );
  cam.lookAt(orb.tx, orb.ty, orb.tz);
}}

// ── Lights
scene.add(new THREE.AmbientLight(0x334466, 0.9));
const sun = new THREE.DirectionalLight(0xffffff,1.4);
sun.position.set(10,18,8); sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
['left','right','top','bottom'].forEach((s,i)=>sun.shadow.camera[s]=[-20,20,20,-20][i]);
scene.add(sun);
const fill = new THREE.DirectionalLight(0x4488ff,0.4);
fill.position.set(-8,4,-6); scene.add(fill);

// ── Grid + ground
scene.add(new THREE.GridHelper(30,30,0x30363d,0x1a1f27));
const gnd = new THREE.Mesh(
  new THREE.PlaneGeometry(100,100),
  new THREE.MeshBasicMaterial({{visible:false,side:THREE.DoubleSide}})
);
gnd.rotation.x=-Math.PI/2; gnd.name='_ground'; scene.add(gnd);

// ── State
let objects=[], selected=null, transformMode='{mode_js}', colorIdx=0;
const COLORS=[0x4a9eff,0xff6b6b,0x6bffb8,0xffd93d,0xa78bfa,0xfb923c,0x34d399,0xf472b6];
const nameCnt={{}};

// ── Gizmo
let gizmoGroup=null;
const gizmoMeshes=[];
const AX_CLR={{x:0xff4444,y:0x44ff44,z:0x4488ff}};

function buildGizmo(){{
  if(gizmoGroup) scene.remove(gizmoGroup);
  gizmoGroup = new THREE.Group(); gizmoGroup.name='_gizmo';
  gizmoMeshes.length=0;
  ['x','y','z'].forEach(ax=>{{
    const shaft=new THREE.Mesh(
      new THREE.CylinderGeometry(0.05,0.05,1.5,8),
      new THREE.MeshBasicMaterial({{color:AX_CLR[ax],depthTest:false}})
    );
    const tip=new THREE.Mesh(
      new THREE.ConeGeometry(0.13,0.38,8),
      new THREE.MeshBasicMaterial({{color:AX_CLR[ax],depthTest:false}})
    );
    tip.position.y=0.94;
    const arr=new THREE.Group(); arr.add(shaft,tip); arr.userData.axis=ax;
    if(ax==='x'){{arr.rotation.z=-Math.PI/2; arr.position.x=0.95;}}
    if(ax==='y'){{arr.position.y=0.95;}}
    if(ax==='z'){{arr.rotation.x=Math.PI/2; arr.position.z=0.95;}}
    gizmoGroup.add(arr); gizmoMeshes.push(arr);
  }});
  scene.add(gizmoGroup);
}}

function syncGizmo(){{
  if(!selected||!gizmoGroup) return;
  gizmoGroup.position.copy(selected.position);
  const s=Math.max(...selected.scale.toArray())*0.55+0.5;
  gizmoGroup.scale.setScalar(s);
}}

// ── Shape geometries
const GEOS={{
  cube:()=>new THREE.BoxGeometry(1.2,1.2,1.2),
  sphere:()=>new THREE.SphereGeometry(0.75,32,32),
  cylinder:()=>new THREE.CylinderGeometry(0.6,0.6,1.5,32),
  cone:()=>new THREE.ConeGeometry(0.7,1.5,32),
  torus:()=>new THREE.TorusGeometry(0.65,0.22,16,64),
  plane:()=>new THREE.PlaneGeometry(2,2),
}};

function addShape(type){{
  nameCnt[type]=(nameCnt[type]||0)+1;
  const mat=new THREE.MeshStandardMaterial({{
    color:COLORS[colorIdx++%COLORS.length],roughness:0.38,metalness:0.18
  }});
  const mesh=new THREE.Mesh(GEOS[type](),mat);
  mesh.castShadow=true; mesh.receiveShadow=true;
  const a=Math.random()*Math.PI*2, r=Math.random()*3;
  mesh.position.set(Math.cos(a)*r,0.8,Math.sin(a)*r);
  mesh.userData={{type,name:type+'_'+nameCnt[type]}};
  scene.add(mesh); objects.push(mesh);
  selectObj(mesh);
  setStatus('Added '+mesh.userData.name);
  pushScene();
}}

function selectObj(obj){{
  if(selected&&selected!==obj) selected.material.emissive.setHex(0x000000);
  selected=obj;
  if(selected){{
    selected.material.emissive.setHex(0x223355);
    buildGizmo(); syncGizmo();
    const p=selected.position;
    setStatus('Selected: '+selected.userData.name+
      ' | ('+p.x.toFixed(2)+', '+p.y.toFixed(2)+', '+p.z.toFixed(2)+')');
  }} else {{
    if(gizmoGroup){{scene.remove(gizmoGroup);gizmoGroup=null;}}
  }}
}}

function deleteSelected(){{
  if(!selected) return setStatus('Nothing selected');
  scene.remove(selected);
  objects=objects.filter(o=>o!==selected);
  if(gizmoGroup){{scene.remove(gizmoGroup);gizmoGroup=null;}}
  selected=null;
  setStatus('Deleted'); pushScene();
}}

function clearScene(){{
  objects.forEach(o=>scene.remove(o));
  objects=[]; colorIdx=0;
  Object.keys(nameCnt).forEach(k=>delete nameCnt[k]);
  if(gizmoGroup){{scene.remove(gizmoGroup);gizmoGroup=null;}}
  selected=null;
  setStatus('Scene cleared'); pushScene();
}}

function setColor(hex){{
  if(!selected) return setStatus('Select an object first');
  selected.material.color.set(hex);
  setStatus('Color applied'); pushScene();
}}

// ── Raycaster
const ray=new THREE.Raycaster(), mpos=new THREE.Vector2();
function getHits(ev,targets){{
  const rc=renderer.domElement.getBoundingClientRect();
  mpos.x=((ev.clientX-rc.left)/rc.width)*2-1;
  mpos.y=-((ev.clientY-rc.top)/rc.height)*2+1;
  ray.setFromCamera(mpos,cam);
  return ray.intersectObjects(targets,true);
}}

// ── Mouse
let isOrb=false,isPan=false,isDrag=false;
let lm={{x:0,y:0}},dm={{x:0,y:0}};
let dragAxis=null,sp=null,sr=null,ss=null;

renderer.domElement.addEventListener('mousedown',e=>{{
  dm={{x:e.clientX,y:e.clientY}};
  if(selected&&gizmoGroup){{
    const all=[]; gizmoGroup.traverse(c=>{{if(c.isMesh)all.push(c);}});
    const hits=getHits(e,all);
    if(hits.length>0){{
      let anc=hits[0].object;
      while(anc.parent&&!anc.userData.axis) anc=anc.parent;
      dragAxis=anc.userData.axis; isDrag=true;
      sp=selected.position.clone(); sr=selected.rotation.clone(); ss=selected.scale.clone();
      lm={{x:e.clientX,y:e.clientY}}; return;
    }}
  }}
  if(e.button===0) isOrb=true;
  if(e.button===2) isPan=true;
  lm={{x:e.clientX,y:e.clientY}};
}});

renderer.domElement.addEventListener('mouseup',e=>{{
  if(isDrag){{isDrag=false;dragAxis=null;pushScene();return;}}
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
      const sc=ss.clone(), f=1+d*1.5;
      if(dragAxis==='x') sc.x=Math.max(0.05,ss.x*f);
      if(dragAxis==='y') sc.y=Math.max(0.05,ss.y*f);
      if(dragAxis==='z') sc.z=Math.max(0.05,ss.z*f);
      selected.scale.copy(sc);
    }}
    syncGizmo(); lm={{x:e.clientX,y:e.clientY}}; return;
  }}
  if(isOrb){{
    orb.theta-=(e.clientX-lm.x)*0.007;
    orb.phi-=(e.clientY-lm.y)*0.007;
    orb.phi=Math.max(0.08,Math.min(Math.PI-0.08,orb.phi));
  }}
  if(isPan){{
    const spd=0.012*(orb.r/10);
    const right=new THREE.Vector3().crossVectors(
      new THREE.Vector3(
        Math.sin(orb.phi)*Math.sin(orb.theta),
        Math.cos(orb.phi),
        Math.sin(orb.phi)*Math.cos(orb.theta)
      ), new THREE.Vector3(0,1,0)
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

// ── Status & scene export
function setStatus(msg){{document.getElementById('status').innerText=msg;}}

function pushScene(){{
  const data=objects.map(o=>{{
    const c=o.material.color;
    return {{
      name:o.userData.name, type:o.userData.type,
      position:o.position.toArray().map(v=>+v.toFixed(3)),
      rotation:[o.rotation.x,o.rotation.y,o.rotation.z].map(v=>+v.toFixed(3)),
      scale:o.scale.toArray().map(v=>+v.toFixed(3)),
      color:'#'+c.getHexString()
    }};
  }});
  // Make available in console for copy-paste
  window._sceneJSON = JSON.stringify(data);
}}

// ── Handle command injected from Python
(function(){{
  const cmd = {js_cmd};
  if(!cmd||cmd==='null') return;
  if(cmd.startsWith('addShape:')) {{ addShape(cmd.split(':')[1]); return; }}
  if(cmd==='deleteSelected') {{ deleteSelected(); return; }}
  if(cmd==='clearScene') {{ clearScene(); return; }}
  if(cmd.startsWith('setColor:')) {{ setColor(cmd.split(':')[1]); return; }}
}})();

// ── Render loop
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

# ── Main area ─────────────────────────────────────────────────
st.markdown("## 🧊 AI 3D Studio")
components.html(HTML, height=620, scrolling=False)

# ── AI Analysis ───────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🤖 AI Design Analysis")

st.info(
    "After building your scene, open the browser console (**F12 → Console**) "
    "and type `_sceneJSON` then press Enter. Copy the output and paste it below.",
    icon="💡"
)

col_left, col_right = st.columns([1,2])

with col_left:
    scene_json = st.text_area(
        "📋 Paste scene JSON here",
        height=200,
        placeholder='[{"name":"cube_1","type":"cube","position":[0,0.8,0],...}]'
    )

with col_right:
    if analyze:
        if not scene_json.strip():
            st.warning("Paste the scene JSON first (see instructions above).")
        else:
            with st.spinner("Claude is analyzing your design..."):
                try:
                    mode_prompts = {
                        "General Design Review":    "Give a holistic design review covering composition, balance, use of space, and overall quality.",
                        "Structural Analysis":      "Analyze structural integrity and spatial logic. Are positions physically sensible?",
                        "Aesthetic & Composition":  "Evaluate color harmony, visual balance, and whether the arrangement is pleasing.",
                        "Optimization Suggestions": "Give specific improvements — repositioning, rescaling, or replacing objects.",
                        "Architecture Critique":    "Critique as an architect: proportions, spatial flow, form relationships.",
                    }
                    try:
                        objs = json.loads(scene_json)
                        desc = f"3D scene with {len(objs)} object(s):\n"
                        for o in objs:
                            desc += (f"\n• {o.get('name','?')} ({o.get('type','?')}) — "
                                     f"pos:{o.get('position','?')} scale:{o.get('scale','?')} "
                                     f"color:{o.get('color','?')}")
                    except Exception:
                        desc = scene_json  # treat as free text if not valid JSON

                    prompt = (
                        f"You are an expert 3D designer and design critic.\n\n"
                        f"Scene:\n{desc}\n\n"
                        f"Task: {mode_prompts[analysis_mode]}\n"
                    )
                    if custom_q.strip():
                        prompt += f"\nAlso answer: {custom_q.strip()}"
                    prompt += "\n\nBe specific, reference object names, use short paragraphs. Max 350 words."

                    client = anthropic.Anthropic(api_key=API_KEY)
                    resp = client.messages.create(
                        model="claude-opus-4-6",
                        max_tokens=700,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.success("✅ Analysis complete")
                    st.markdown(resp.content[0].text)

                except anthropic.AuthenticationError:
                    st.error("❌ Invalid API key. Edit the `API_KEY` variable at the top of `app.py`.")
                except Exception as ex:
                    st.error(f"❌ Error: {ex}")
    else:
        st.markdown(
            "_Build a scene above, paste the JSON from the browser console, "
            "then click **🔍 Analyze with Claude** in the sidebar._"
        )