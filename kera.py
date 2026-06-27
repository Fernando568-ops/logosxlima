python3 - << 'PYEOF'
# Write the app using a pure WebGL renderer built from scratch - no external deps
code = r'''import streamlit as st
import streamlit.components.v1 as components
import json, requests

try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    API_KEY = ""

st.set_page_config(page_title="CAD AI Studio", layout="wide", page_icon="🔩")
st.markdown("""
<style>
body,.stApp{background:#0d1117!important;color:#e6edf3;}
[data-testid="stSidebar"]{background:#161b22!important;border-right:1px solid #30363d;}
[data-testid="stSidebar"] *{color:#c9d1d9!important;}
.stButton>button{background:#21262d!important;color:#c9d1d9!important;border:1px solid #30363d!important;
  border-radius:6px!important;font-size:12px!important;width:100%!important;margin:2px 0!important;}
.stButton>button:hover{background:#1f6feb!important;color:#fff!important;}
footer,header,#MainMenu{visibility:hidden;}
.block-container{padding-top:0.5rem!important;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🔩 CAD AI Studio")
    if not API_KEY:
        st.warning("Set OPENAI_API_KEY in Streamlit Secrets")
    else:
        st.success("✓ API key loaded")
    st.markdown("---")
    st.markdown("### ➕ Primitives")
    c1,c2=st.columns(2)
    with c1:
        add_box      = st.button("⬛ Box")
        add_cylinder = st.button("🔵 Cylinder")
        add_cone     = st.button("🔺 Cone")
        add_wedge    = st.button("◺ Wedge")
    with c2:
        add_sphere   = st.button("⚪ Sphere")
        add_torus    = st.button("⭕ Torus")
        add_pyramid  = st.button("△ Pyramid")
        add_capsule  = st.button("💊 Capsule")
    st.markdown("---")
    st.markdown("### 🔧 CAD Ops")
    c3,c4=st.columns(2)
    with c3:
        do_extrude   = st.button("↑ Extrude")
        do_duplicate = st.button("⧉ Duplicate")
        do_mirrorX   = st.button("⟺ Mirror X")
    with c4:
        do_flatten   = st.button("⬓ Flatten")
        do_taper     = st.button("⊿ Taper")
        do_mirrorZ   = st.button("⟺ Mirror Z")
    st.markdown("---")
    st.markdown("### 🎮 Transform")
    mode = st.radio("", ["Move","Rotate","Scale"], horizontal=True, label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### 📐 Precise")
    px=st.number_input("Pos X",value=0.0,step=0.5,format="%.2f")
    py=st.number_input("Pos Y",value=0.0,step=0.5,format="%.2f")
    pz=st.number_input("Pos Z",value=0.0,step=0.5,format="%.2f")
    apply_pos=st.button("Apply Position")
    sx=st.number_input("Scale X",value=1.0,step=0.1,format="%.2f")
    sy=st.number_input("Scale Y",value=1.0,step=0.1,format="%.2f")
    sz=st.number_input("Scale Z",value=1.0,step=0.1,format="%.2f")
    apply_scale=st.button("Apply Scale")
    st.markdown("---")
    st.markdown("### 📏 Snap")
    snap_on=st.checkbox("Snap to Grid",value=True)
    grid_sz=st.selectbox("Grid Size",[0.25,0.5,1.0,2.0],index=2)
    st.markdown("---")
    st.markdown("### 🎨 Appearance")
    color_pick=st.color_picker("Color","#4a9eff")
    apply_color=st.button("Apply Color")
    wireframe=st.checkbox("Wireframe")
    st.markdown("---")
    st.markdown("### 🗑 Scene")
    delete_sel=st.button("🗑 Delete")
    clear_all=st.button("✕ Clear All")
    st.markdown("---")
    st.markdown("### 🤖 AI")
    amode=st.selectbox("",[
        "General Design Review","Structural Analysis",
        "CAD Optimization","Manufacturability","Architecture Critique"
    ],label_visibility="collapsed")

js_cmd="null"
if add_box:       js_cmd="'add:box'"
elif add_sphere:  js_cmd="'add:sphere'"
elif add_cylinder:js_cmd="'add:cylinder'"
elif add_cone:    js_cmd="'add:cone'"
elif add_torus:   js_cmd="'add:torus'"
elif add_wedge:   js_cmd="'add:wedge'"
elif add_pyramid: js_cmd="'add:pyramid'"
elif add_capsule: js_cmd="'add:capsule'"
elif do_extrude:  js_cmd="'cad:extrude'"
elif do_duplicate:js_cmd="'cad:duplicate'"
elif do_mirrorX:  js_cmd="'cad:mirrorX'"
elif do_mirrorZ:  js_cmd="'cad:mirrorZ'"
elif do_flatten:  js_cmd="'cad:flatten'"
elif do_taper:    js_cmd="'cad:taper'"
elif delete_sel:  js_cmd="'delete'"
elif clear_all:   js_cmd="'clear'"
elif apply_color: js_cmd=f"'color:{color_pick}'"
elif apply_pos:   js_cmd=f"'pos:{px},{py},{pz}'"
elif apply_scale: js_cmd=f"'scale:{sx},{sy},{sz}'"

mode_js={"Move":"move","Rotate":"rotate","Scale":"scale"}[mode]

# AI via Python server
if "ai_result" not in st.session_state: st.session_state.ai_result=""
if "ai_obj"    not in st.session_state: st.session_state.ai_obj=""

sel_raw=st.query_params.get("analyze","")
if sel_raw and sel_raw!=st.session_state.ai_obj and API_KEY:
    st.session_state.ai_obj=sel_raw
    try:
        obj=json.loads(sel_raw)
        prompts={"General Design Review":"Review placement, scale, role in scene.",
                 "Structural Analysis":"Analyze structural integrity and spatial logic.",
                 "CAD Optimization":"Give specific CAD improvements.",
                 "Manufacturability":"Assess manufacturability, note concerns.",
                 "Architecture Critique":"Critique proportions, placement, form."}
        prompt=f"""Expert CAD designer analyzing:
Name:{obj.get('name')} Type:{obj.get('type')}
Position:{obj.get('position')} Scale:{obj.get('scale')} Color:{obj.get('color')}
Scene total:{obj.get('total')} objects
Task:{prompts.get(amode,'Review this object.')}
Be specific, 3-4 short paragraphs."""
        r=requests.post("https://api.openai.com/v1/chat/completions",
            headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},
            json={"model":"gpt-4o-mini","max_tokens":500,
                  "messages":[{"role":"user","content":prompt}]},timeout=30)
        d=r.json()
        st.session_state.ai_result=d["choices"][0]["message"]["content"] if r.status_code==200 else f"ERROR:{d.get('error',{}).get('message','')}"
    except Exception as e:
        st.session_state.ai_result=f"ERROR:{e}"

ai_result_js=json.dumps(st.session_state.ai_result)
ai_obj_js=json.dumps(st.session_state.ai_obj)

HTML=f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#0d1117;overflow:hidden;font-family:monospace;}}
canvas{{display:block;width:100%;height:100%;}}
#hud{{position:absolute;top:10px;left:10px;background:#161b22cc;border:1px solid #30363d;
  border-radius:6px;padding:8px 12px;font-size:10px;color:#8b949e;line-height:2;pointer-events:none;}}
#status{{position:absolute;bottom:60px;left:10px;right:10px;text-align:center;
  background:#161b22cc;border:1px solid #30363d;border-radius:6px;
  padding:5px 12px;font-size:11px;color:#c9d1d9;pointer-events:none;}}
#dims{{position:absolute;top:10px;right:10px;background:#161b22cc;border:1px solid #30363d;
  border-radius:6px;padding:8px 12px;font-size:10px;color:#8b949e;display:none;line-height:1.9;}}
#analyze-btn{{position:absolute;bottom:12px;left:50%;transform:translateX(-50%);
  background:#1f6feb;color:#fff;border:none;border-radius:6px;padding:8px 26px;
  font-size:13px;font-family:monospace;cursor:pointer;display:none;}}
#analyze-btn:hover{{background:#388bfd;}}
#ai-panel{{position:absolute;top:10px;right:10px;width:300px;
  background:#161b22f0;border:1px solid #30363d;border-radius:8px;
  display:none;flex-direction:column;max-height:calc(100% - 80px);}}
#ai-hdr{{display:flex;align-items:center;justify-content:space-between;
  padding:9px 13px;border-bottom:1px solid #30363d;}}
#ai-hdr span{{color:#58a6ff;font-size:11px;text-transform:uppercase;letter-spacing:.07em;}}
#ai-close{{background:none;border:none;color:#8b949e;cursor:pointer;font-size:15px;}}
#ai-body{{padding:13px;overflow-y:auto;flex:1;font-size:12px;color:#c9d1d9;line-height:1.75;}}
.otag{{background:#1f6feb22;border:1px solid #1f6feb44;border-radius:4px;
  padding:2px 8px;font-size:10px;color:#58a6ff;margin-bottom:10px;display:inline-block;}}
.ap{{margin-bottom:9px;}}
.err{{color:#ff6b6b;}}
.loading{{color:#8b949e;}}
</style></head><body>
<canvas id="c"></canvas>
<div id="hud">Left-drag · Orbit &nbsp;|&nbsp; Right-drag · Pan &nbsp;|&nbsp; Scroll · Zoom<br>
Click · Select &nbsp;|&nbsp; Drag arrows · Transform &nbsp;|&nbsp; <b>X</b> · AI Analyze<br>
Mode: <b>{mode}</b> &nbsp;|&nbsp; Snap: <b>{"ON" if snap_on else "OFF"}</b></div>
<div id="status">Ready — add shapes from the sidebar</div>
<div id="dims"></div>
<button id="analyze-btn" onclick="triggerAnalyze()">🔍 Analyze (X)</button>
<div id="ai-panel">
  <div id="ai-hdr"><span>🤖 AI Analysis</span><button id="ai-close" onclick="closeAI()">✕</button></div>
  <div id="ai-body"><div class="loading">Loading...</div></div>
</div>
<script>
// ══════════════════════════════════════════════════════════════
//  PURE WebGL 3D ENGINE — zero external dependencies
// ══════════════════════════════════════════════════════════════
const canvas = document.getElementById('c');
const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
if(!gl){{ document.getElementById('status').innerText='WebGL not supported in this browser'; }}

// ── Resize
function resize(){{
  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight;
  gl.viewport(0, 0, canvas.width, canvas.height);
}}
window.addEventListener('resize', resize);
resize();

// ── Shaders
const vsrc = `
  attribute vec3 aPos;
  attribute vec3 aNorm;
  uniform mat4 uMVP;
  uniform mat4 uModel;
  uniform mat3 uNormMat;
  varying vec3 vNorm;
  varying vec3 vPos;
  void main(){{
    vec4 worldPos = uModel * vec4(aPos,1.0);
    vPos  = worldPos.xyz;
    vNorm = normalize(uNormMat * aNorm);
    gl_Position = uMVP * vec4(aPos,1.0);
  }}
`;
const fsrc = `
  precision mediump float;
  varying vec3 vNorm;
  varying vec3 vPos;
  uniform vec3  uColor;
  uniform bool  uWire;
  uniform vec3  uSel;   // selection highlight
  void main(){{
    vec3 light1 = normalize(vec3(0.6,1.0,0.5));
    vec3 light2 = normalize(vec3(-0.4,0.3,-0.6));
    float d1 = max(dot(vNorm,light1),0.0)*0.8;
    float d2 = max(dot(vNorm,light2),0.0)*0.25;
    float amb= 0.32;
    vec3  col = uColor*(amb+d1+d2);
    col += uSel*0.18;
    gl_FragColor = vec4(col,1.0);
  }}
`;
const lvsrc = `
  attribute vec3 aPos;
  uniform mat4 uMVP;
  void main(){{ gl_Position = uMVP * vec4(aPos,1.0); }}
`;
const lfsrc = `
  precision mediump float;
  uniform vec3 uColor;
  void main(){{ gl_FragColor = vec4(uColor,1.0); }}
`;

function compileShader(src, type){{
  const s = gl.createShader(type);
  gl.shaderSource(s, src);
  gl.compileShader(s);
  return s;
}}
function makeProgram(vs, fs){{
  const p = gl.createProgram();
  gl.attachShader(p, compileShader(vs, gl.VERTEX_SHADER));
  gl.attachShader(p, compileShader(fs, gl.FRAGMENT_SHADER));
  gl.linkProgram(p);
  return p;
}}
const prog  = makeProgram(vsrc, fsrc);
const lprog = makeProgram(lvsrc, lfsrc);

// ── Math helpers
function mat4(){{ return new Float32Array(16); }}
function identity(m){{
  m[0]=1;m[1]=0;m[2]=0;m[3]=0;
  m[4]=0;m[5]=1;m[6]=0;m[7]=0;
  m[8]=0;m[9]=0;m[10]=1;m[11]=0;
  m[12]=0;m[13]=0;m[14]=0;m[15]=1;
  return m;
}}
function perspective(m,fov,asp,near,far){{
  const f=1/Math.tan(fov/2), nf=1/(near-far);
  m[0]=f/asp;m[1]=0;m[2]=0;m[3]=0;
  m[4]=0;m[5]=f;m[6]=0;m[7]=0;
  m[8]=0;m[9]=0;m[10]=(far+near)*nf;m[11]=-1;
  m[12]=0;m[13]=0;m[14]=2*far*near*nf;m[15]=0;
  return m;
}}
function lookAt(m,ex,ey,ez,cx,cy,cz){{
  let fx=cx-ex,fy=cy-ey,fz=cz-ez;
  let l=Math.sqrt(fx*fx+fy*fy+fz*fz);
  fx/=l;fy/=l;fz/=l;
  let rx=fy*0-fz*1,ry=fz*0-fx*0,rz=fx*1-fy*0;
  l=Math.sqrt(rx*rx+ry*ry+rz*rz);
  if(l>0){{rx/=l;ry/=l;rz/=l;}}
  let ux=ry*fz-rz*fy,uy=rz*fx-rx*fz,uz=rx*fy-ry*fx;
  m[0]=rx;m[1]=ux;m[2]=-fx;m[3]=0;
  m[4]=ry;m[5]=uy;m[6]=-fy;m[7]=0;
  m[8]=rz;m[9]=uz;m[10]=-fz;m[11]=0;
  m[12]=-(rx*ex+ry*ey+rz*ez);
  m[13]=-(ux*ex+uy*ey+uz*ez);
  m[14]=fx*ex+fy*ey+fz*ez;m[15]=1;
  return m;
}}
function mul(out,a,b){{
  for(let i=0;i<4;i++) for(let j=0;j<4;j++){{
    out[j*4+i]=0;
    for(let k=0;k<4;k++) out[j*4+i]+=a[k*4+i]*b[j*4+k];
  }}
  return out;
}}
function makeModel(px,py,pz,rx,ry,rz,sx,sy,sz){{
  const m=mat4();identity(m);
  // Scale
  const ms=mat4();identity(ms);ms[0]=sx;ms[5]=sy;ms[10]=sz;
  // RotX
  const mx=mat4();identity(mx);
  mx[5]=Math.cos(rx);mx[6]=Math.sin(rx);mx[9]=-Math.sin(rx);mx[10]=Math.cos(rx);
  // RotY
  const my=mat4();identity(my);
  my[0]=Math.cos(ry);my[2]=-Math.sin(ry);my[8]=Math.sin(ry);my[10]=Math.cos(ry);
  // RotZ
  const mz=mat4();identity(mz);
  mz[0]=Math.cos(rz);mz[1]=Math.sin(rz);mz[4]=-Math.sin(rz);mz[5]=Math.cos(rz);
  // Trans
  const mt=mat4();identity(mt);mt[12]=px;mt[13]=py;mt[14]=pz;
  const tmp=mat4(),tmp2=mat4(),tmp3=mat4(),tmp4=mat4();
  mul(tmp,my,mx); mul(tmp2,mz,tmp); mul(tmp3,tmp2,ms); mul(tmp4,mt,tmp3);
  return tmp4;
}}
function normMat(m){{
  // 3x3 inverse transpose of upper-left of model
  const a=m[0],b=m[4],c=m[8],
        d=m[1],e=m[5],f=m[9],
        g=m[2],h=m[6],k=m[10];
  const det=a*(e*k-f*h)-b*(d*k-f*g)+c*(d*h-e*g);
  const id=1/det;
  return new Float32Array([
    (e*k-f*h)*id,(f*g-d*k)*id,(d*h-e*g)*id,
    (c*h-b*k)*id,(a*k-c*g)*id,(b*g-a*h)*id,
    (b*f-c*e)*id,(c*d-a*f)*id,(a*e-b*d)*id
  ]);
}}

// ── Geometry builders
function buildBox(){{
  const p=[],n=[],idx=[];
  const faces=[
    [0,0,1],[0,0,-1],[0,1,0],[0,-1,0],[1,0,0],[-1,0,0]
  ];
  faces.forEach((nm,fi)=>{{
    const [nx,ny,nz]=nm;
    // build quad verts based on normal
    let u=[0,0,0],v=[0,0,0];
    if(Math.abs(nx)>0.5){{u=[0,1,0];v=[0,0,1];}}
    else if(Math.abs(ny)>0.5){{u=[1,0,0];v=[0,0,1];}}
    else{{u=[1,0,0];v=[0,1,0];}}
    const base=p.length/3;
    for(let s=-1;s<=1;s+=2) for(let t=-1;t<=1;t+=2){{
      p.push(nx*0.5+u[0]*s*0.5+v[0]*t*0.5,
             ny*0.5+u[1]*s*0.5+v[1]*t*0.5,
             nz*0.5+u[2]*s*0.5+v[2]*t*0.5);
      n.push(nx,ny,nz);
    }}
    idx.push(base,base+1,base+2,base+1,base+3,base+2);
  }});
  return {{pos:new Float32Array(p),norm:new Float32Array(n),idx:new Uint16Array(idx)}};
}}
function buildSphere(segs=20){{
  const p=[],n=[],idx=[];
  for(let lat=0;lat<=segs;lat++){{
    const phi=Math.PI*lat/segs;
    for(let lon=0;lon<=segs;lon++){{
      const theta=2*Math.PI*lon/segs;
      const x=Math.sin(phi)*Math.cos(theta);
      const y=Math.cos(phi);
      const z=Math.sin(phi)*Math.sin(theta);
      p.push(x*0.6,y*0.6,z*0.6);n.push(x,y,z);
    }}
  }}
  for(let lat=0;lat<segs;lat++) for(let lon=0;lon<segs;lon++){{
    const a=lat*(segs+1)+lon,b=a+segs+1;
    idx.push(a,b,a+1,b,b+1,a+1);
  }}
  return {{pos:new Float32Array(p),norm:new Float32Array(n),idx:new Uint16Array(idx)}};
}}
function buildCylinder(segs=24){{
  const p=[],n=[],idx=[];
  // side
  for(let i=0;i<=segs;i++){{
    const a=2*Math.PI*i/segs,cx=Math.cos(a),cz=Math.sin(a);
    p.push(cx*0.6,-0.75,cz*0.6);n.push(cx,0,cz);
    p.push(cx*0.6, 0.75,cz*0.6);n.push(cx,0,cz);
  }}
  for(let i=0;i<segs;i++){{
    const b=i*2;idx.push(b,b+1,b+2,b+1,b+3,b+2);
  }}
  // caps
  const tc=p.length/3;
  p.push(0,-0.75,0);n.push(0,-1,0);
  for(let i=0;i<segs;i++){{
    const a=2*Math.PI*i/segs;
    p.push(Math.cos(a)*0.6,-0.75,Math.sin(a)*0.6);n.push(0,-1,0);
  }}
  for(let i=0;i<segs-1;i++) idx.push(tc,tc+i+1,tc+i+2);
  idx.push(tc,tc+segs,tc+1);
  const bc=p.length/3;
  p.push(0,0.75,0);n.push(0,1,0);
  for(let i=0;i<segs;i++){{
    const a=2*Math.PI*i/segs;
    p.push(Math.cos(a)*0.6,0.75,Math.sin(a)*0.6);n.push(0,1,0);
  }}
  for(let i=0;i<segs-1;i++) idx.push(bc,bc+i+2,bc+i+1);
  idx.push(bc,bc+1,bc+segs);
  return {{pos:new Float32Array(p),norm:new Float32Array(n),idx:new Uint16Array(idx)}};
}}
function buildCone(segs=24){{
  const p=[],n=[],idx=[];
  for(let i=0;i<=segs;i++){{
    const a=2*Math.PI*i/segs,cx=Math.cos(a),cz=Math.sin(a);
    const sl=Math.sqrt(0.36+0.5625);
    p.push(cx*0.6,-0.75,cz*0.6);n.push(cx*0.75/sl,0.6/sl,cz*0.75/sl);
    p.push(0,0.75,0);n.push(cx*0.75/sl,0.6/sl,cz*0.75/sl);
  }}
  for(let i=0;i<segs;i++){{const b=i*2;idx.push(b,b+2,b+1);}}
  const base=p.length/3;
  p.push(0,-0.75,0);n.push(0,-1,0);
  for(let i=0;i<segs;i++){{
    const a=2*Math.PI*i/segs;
    p.push(Math.cos(a)*0.6,-0.75,Math.sin(a)*0.6);n.push(0,-1,0);
  }}
  for(let i=0;i<segs-1;i++) idx.push(base,base+i+2,base+i+1);
  idx.push(base,base+1,base+segs);
  return {{pos:new Float32Array(p),norm:new Float32Array(n),idx:new Uint16Array(idx)}};
}}
function buildTorus(R=0.55,r=0.2,segsR=24,segsr=16){{
  const p=[],n=[],idx=[];
  for(let i=0;i<=segsR;i++){{
    const phi=2*Math.PI*i/segsR,cp=Math.cos(phi),sp=Math.sin(phi);
    for(let j=0;j<=segsr;j++){{
      const theta=2*Math.PI*j/segsr,ct=Math.cos(theta),st=Math.sin(theta);
      const x=(R+r*ct)*cp,y=r*st,z=(R+r*ct)*sp;
      p.push(x,y,z);n.push(ct*cp,st,ct*sp);
    }}
  }}
  for(let i=0;i<segsR;i++) for(let j=0;j<segsr;j++){{
    const a=i*(segsr+1)+j,b=a+segsr+1;
    idx.push(a,b,a+1,b,b+1,a+1);
  }}
  return {{pos:new Float32Array(p),norm:new Float32Array(n),idx:new Uint16Array(idx)}};
}}
function buildWedge(){{
  // 5-face wedge: triangle prism
  const p=[],n=[],idx=[];
  const verts=[
    [-0.6,-0.6,-0.6],[ 0.6,-0.6,-0.6],[ 0.6,-0.6, 0.6],[-0.6,-0.6, 0.6],
    [-0.6, 0.6, 0.6],[ 0.6, 0.6, 0.6]
  ];
  const faces=[
    [0,1,2,3,[0,-1,0]],[4,5,2,3,[0,0,1]],
    [0,1,5,4,[0,0.6,-0.8]],
    [0,3,4,0,[0,0.6,-0.8]],[1,2,5,1,[0,0.6,-0.8]]
  ];
  // Bottom
  const base=p.length/3;
  [0,1,2,3].forEach(i=>{{p.push(...verts[i]);n.push(0,-1,0);}});
  idx.push(base,base+1,base+2,base,base+2,base+3);
  // Back
  const back=p.length/3;
  [4,5,2,3].forEach(i=>{{p.push(...verts[i]);n.push(0,0,1);}});
  idx.push(back,back+1,back+2,back,back+2,back+3);
  // Slope
  const sl=p.length/3;
  [0,1,5,4].forEach(i=>{{p.push(...verts[i]);n.push(0,0.8,-0.6);}});
  idx.push(sl,sl+1,sl+2,sl,sl+2,sl+3);
  // Left
  const lf=p.length/3;
  [0,3,4,0].forEach(i=>{{p.push(...verts[i]);n.push(-1,0,0);}});
  idx.push(lf,lf+1,lf+2);
  // Right
  const rf=p.length/3;
  [1,2,5,1].forEach(i=>{{p.push(...verts[i]);n.push(1,0,0);}});
  idx.push(rf,rf+1,rf+2);
  return {{pos:new Float32Array(p),norm:new Float32Array(n),idx:new Uint16Array(idx)}};
}}
function buildPyramid(segs=4){{
  const p=[],n=[],idx=[];
  // Base
  const base=p.length/3;
  p.push(0,-0.7,0);n.push(0,-1,0);
  for(let i=0;i<segs;i++){{
    const a=2*Math.PI*i/segs;
    p.push(Math.cos(a)*0.7,-0.7,Math.sin(a)*0.7);n.push(0,-1,0);
  }}
  for(let i=0;i<segs-1;i++) idx.push(base,base+i+2,base+i+1);
  idx.push(base,base+1,base+segs);
  // Sides
  for(let i=0;i<segs;i++){{
    const a0=2*Math.PI*i/segs,a1=2*Math.PI*(i+1)/segs;
    const x0=Math.cos(a0)*0.7,z0=Math.sin(a0)*0.7;
    const x1=Math.cos(a1)*0.7,z1=Math.sin(a1)*0.7;
    const nx=(z1-z0)*0.7,nz=-(x1-x0)*0.7,ny=0.5;
    const l=Math.sqrt(nx*nx+ny*ny+nz*nz);
    const b=p.length/3;
    p.push(x0,-0.7,z0,x1,-0.7,z1,0,0.7,0);
    n.push(nx/l,ny/l,nz/l,nx/l,ny/l,nz/l,nx/l,ny/l,nz/l);
    idx.push(b,b+1,b+2);
  }}
  return {{pos:new Float32Array(p),norm:new Float32Array(n),idx:new Uint16Array(idx)}};
}}
function buildCapsule(segs=20){{
  // Cylinder + two hemispherical caps
  const p=[],n=[],idx=[];
  const hemi=(start,dir)=>{{
    for(let lat=0;lat<=segs/2;lat++){{
      const phi=Math.PI/2*lat/(segs/2);
      for(let lon=0;lon<=segs;lon++){{
        const theta=2*Math.PI*lon/segs;
        const x=Math.cos(phi)*Math.cos(theta)*0.5;
        const y=dir*(Math.sin(phi)*0.5+start);
        const z=Math.cos(phi)*Math.sin(theta)*0.5;
        const nx=Math.cos(phi)*Math.cos(theta);
        const ny=dir*Math.sin(phi);
        const nz=Math.cos(phi)*Math.sin(theta);
        p.push(x,y,z);n.push(nx,ny,nz);
      }}
    }}
  }};
  hemi(0.4,1);
  const o1=p.length/3;
  hemi(0.4,-1);
  // side
  const o2=p.length/3;
  for(let i=0;i<=segs;i++){{
    const a=2*Math.PI*i/segs;
    p.push(Math.cos(a)*0.5,-0.4,Math.sin(a)*0.5);n.push(Math.cos(a),0,Math.sin(a));
    p.push(Math.cos(a)*0.5, 0.4,Math.sin(a)*0.5);n.push(Math.cos(a),0,Math.sin(a));
  }}
  const half=segs/2+1;
  for(let lat=0;lat<segs/2;lat++) for(let lon=0;lon<segs;lon++){{
    const a=lat*(segs+1)+lon,b=a+segs+1;
    idx.push(a,b,a+1,b,b+1,a+1);
    idx.push(o1+a,o1+a+1,o1+b,o1+b,o1+a+1,o1+b+1);
  }}
  for(let i=0;i<segs;i++){{
    const b=o2+i*2;idx.push(b,b+1,b+2,b+1,b+3,b+2);
  }}
  return {{pos:new Float32Array(p),norm:new Float32Array(n),idx:new Uint16Array(idx)}};
}}

const GEOS={{
  box:buildBox, sphere:buildSphere, cylinder:buildCylinder,
  cone:buildCone, torus:buildTorus, wedge:buildWedge,
  pyramid:buildPyramid, capsule:buildCapsule
}};

// ── Upload geometry to GPU
function uploadGeo(geo){{
  const pb=gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER,pb);
  gl.bufferData(gl.ARRAY_BUFFER,geo.pos,gl.STATIC_DRAW);
  const nb=gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER,nb);
  gl.bufferData(gl.ARRAY_BUFFER,geo.norm,gl.STATIC_DRAW);
  const ib=gl.createBuffer();
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);
  gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,geo.idx,gl.STATIC_DRAW);
  return {{pb,nb,ib,count:geo.idx.length}};
}}

// Pre-upload all geometries
const GEO_CACHE={{}};
Object.keys(GEOS).forEach(k=>{{GEO_CACHE[k]=uploadGeo(GEOS[k]());}});

// ── Line buffers for grid + gizmo
function makeLineBuf(verts){{
  const b=gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER,b);
  gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(verts),gl.STATIC_DRAW);
  return {{buf:b,count:verts.length/3}};
}}

// Grid lines
const gridLines=[];
const G=10,GS=1;
for(let i=-G;i<=G;i+=GS){{
  gridLines.push(i,0,-G, i,0,G, -G,0,i, G,0,i);
}}
const gridBuf=makeLineBuf(gridLines);

// Gizmo arrow lines
function makeGizmoBufs(){{
  return [
    {{buf:makeLineBuf([0,0,0,1.8,0,0]),color:[1,0.2,0.2],axis:'x'}},
    {{buf:makeLineBuf([0,0,0,0,1.8,0]),color:[0.2,1,0.2],axis:'y'}},
    {{buf:makeLineBuf([0,0,0,0,0,1.8]),color:[0.2,0.5,1],axis:'z'}},
  ];
}}
const gizmoBufs=makeGizmoBufs();

// ── Scene objects
let objects=[], selected=null, transformMode='{mode_js}';
let snapEnabled={snap_js}, gridSize={grid_js}, wireframeMode={wire_js};
let colorIdx=0;
const COLORS=[[0.29,0.61,1],[1,0.42,0.42],[0.42,1,0.72],[1,0.85,0.24],
              [0.65,0.55,0.98],[0.98,0.57,0.19],[0.2,0.83,0.6],[0.98,0.66,0.85]];
const nameCnt={{}};
function snap(v){{return snapEnabled?Math.round(v/gridSize)*gridSize:v;}}

function hexToRgb(hex){{
  const r=parseInt(hex.slice(1,3),16)/255;
  const g=parseInt(hex.slice(3,5),16)/255;
  const b=parseInt(hex.slice(5,7),16)/255;
  return [r,g,b];
}}
function rgbToHex(r,g,b){{
  return '#'+[r,g,b].map(v=>Math.round(v*255).toString(16).padStart(2,'0')).join('');
}}

function addShape(type){{
  nameCnt[type]=(nameCnt[type]||0)+1;
  const col=COLORS[colorIdx++%COLORS.length];
  const a=Math.random()*Math.PI*2,r=Math.random()*3;
  const obj={{
    type, name:type+'_'+nameCnt[type],
    px:snap(Math.cos(a)*r), py:0.8, pz:snap(Math.sin(a)*r),
    rx:0,ry:0,rz:0, sx:1,sy:1,sz:1,
    color:[...col], geo:GEO_CACHE[type],
    id:Date.now()+Math.random()
  }};
  objects.push(obj);
  selectObj(obj);
  setStatus('Added '+obj.name+' — X to analyze');
}}

function selectObj(obj){{
  selected=obj;
  const btn=document.getElementById('analyze-btn');
  if(obj){{
    setStatus('✓ '+obj.name+' | X to analyze with AI');
    btn.style.display='block';
    showDims(obj);
  }} else {{
    btn.style.display='none';
    document.getElementById('dims').style.display='none';
    setStatus('Ready');
  }}
}}

function deleteSelected(){{
  if(!selected)return;
  objects=objects.filter(o=>o!==selected);
  selected=null;
  document.getElementById('analyze-btn').style.display='none';
  document.getElementById('dims').style.display='none';
  closeAI();setStatus('Deleted');
}}

function clearScene(){{
  objects=[];selected=null;colorIdx=0;
  Object.keys(nameCnt).forEach(k=>delete nameCnt[k]);
  document.getElementById('analyze-btn').style.display='none';
  document.getElementById('dims').style.display='none';
  closeAI();setStatus('Scene cleared');
}}

function setColor(hex){{
  if(!selected)return;
  selected.color=hexToRgb(hex);
  setStatus('Color applied');
}}

function applyPos(x,y,z){{
  if(!selected)return;
  selected.px=parseFloat(x);selected.py=parseFloat(y);selected.pz=parseFloat(z);
  showDims(selected);setStatus('Position applied');
}}

function applyScaleFn(x,y,z){{
  if(!selected)return;
  selected.sx=parseFloat(x);selected.sy=parseFloat(y);selected.sz=parseFloat(z);
  showDims(selected);setStatus('Scale applied');
}}

// ── CAD ops
function cadOp(op){{
  if(!selected)return setStatus('Select an object first');
  switch(op){{
    case 'extrude': selected.sy*=2; setStatus('Extruded '+selected.name); break;
    case 'flatten': selected.sy=Math.max(0.05,selected.sy*0.25); setStatus('Flattened'); break;
    case 'taper':   selected.sx*=0.6; selected.sz*=0.6; setStatus('Tapered'); break;
    case 'mirrorX': selected.sx*=-1; setStatus('Mirrored X'); break;
    case 'mirrorZ': selected.sz*=-1; setStatus('Mirrored Z'); break;
    case 'duplicate':
      const copy={{...selected,
        name:selected.type+'_'+(++nameCnt[selected.type]),
        px:selected.px+1.8, id:Date.now()+Math.random(),
        color:[...selected.color]
      }};
      objects.push(copy);selectObj(copy);
      setStatus('Duplicated → '+copy.name);break;
  }}
  showDims(selected);
}}

function showDims(obj){{
  if(!obj){{document.getElementById('dims').style.display='none';return;}}
  const el=document.getElementById('dims');
  el.style.display='block';
  // Approximate bounding box from scale
  const w=(obj.sx*1.2).toFixed(3),h=(obj.sy*1.2).toFixed(3),d=(obj.sz*1.2).toFixed(3);
  el.innerHTML=`<b>${{obj.name}}</b><br>
  W:${{w}} H:${{h}} D:${{d}}<br>
  X:${{obj.px.toFixed(3)}} Y:${{obj.py.toFixed(3)}} Z:${{obj.pz.toFixed(3)}}`;
}}

// ── Camera orbit
const orb={{theta:0.6,phi:1.1,r:16,tx:0,ty:0,tz:0}};
function camPos(){{
  return [
    orb.tx+orb.r*Math.sin(orb.phi)*Math.sin(orb.theta),
    orb.ty+orb.r*Math.cos(orb.phi),
    orb.tz+orb.r*Math.sin(orb.phi)*Math.cos(orb.theta)
  ];
}}

// ── Render
const proj=mat4(),view=mat4(),mvp=mat4(),tmp=mat4();
function render(){{
  gl.clearColor(0.05,0.067,0.09,1);
  gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
  gl.enable(gl.DEPTH_TEST);
  gl.enable(gl.CULL_FACE);

  perspective(proj,Math.PI/3,canvas.width/canvas.height,0.1,200);
  const [ex,ey,ez]=camPos();
  lookAt(view,ex,ey,ez,orb.tx,orb.ty,orb.tz);

  // ── Draw grid (lines)
  gl.useProgram(lprog);
  mul(mvp,proj,view);
  gl.uniformMatrix4fv(gl.getUniformLocation(lprog,'uMVP'),false,mvp);
  gl.uniform3fv(gl.getUniformLocation(lprog,'uColor'),new Float32Array([0.19,0.22,0.27]));
  gl.bindBuffer(gl.ARRAY_BUFFER,gridBuf.buf);
  const lpos=gl.getAttribLocation(lprog,'aPos');
  gl.enableVertexAttribArray(lpos);
  gl.vertexAttribPointer(lpos,3,gl.FLOAT,false,0,0);
  gl.drawArrays(gl.LINES,0,gridBuf.count);

  // ── Draw objects
  gl.useProgram(prog);
  const uMVP=gl.getUniformLocation(prog,'uMVP');
  const uModel=gl.getUniformLocation(prog,'uModel');
  const uNorm=gl.getUniformLocation(prog,'uNormMat');
  const uColor=gl.getUniformLocation(prog,'uColor');
  const uSel=gl.getUniformLocation(prog,'uSel');
  const aPos=gl.getAttribLocation(prog,'aPos');
  const aNorm=gl.getAttribLocation(prog,'aNorm');

  objects.forEach(obj=>{{
    const model=makeModel(obj.px,obj.py,obj.pz,obj.rx,obj.ry,obj.rz,obj.sx,obj.sy,obj.sz);
    mul(mvp,proj,view); mul(tmp,mvp,model);
    gl.uniformMatrix4fv(uMVP,false,tmp);
    gl.uniformMatrix4fv(uModel,false,model);
    gl.uniformMatrix3fv(uNorm,false,normMat(model));
    gl.uniform3fv(uColor,new Float32Array(obj.color));
    gl.uniform3fv(uSel,obj===selected?new Float32Array([0.1,0.2,0.5]):new Float32Array([0,0,0]));

    const g=obj.geo;
    gl.bindBuffer(gl.ARRAY_BUFFER,g.pb);
    gl.enableVertexAttribArray(aPos);
    gl.vertexAttribPointer(aPos,3,gl.FLOAT,false,0,0);
    gl.bindBuffer(gl.ARRAY_BUFFER,g.nb);
    gl.enableVertexAttribArray(aNorm);
    gl.vertexAttribPointer(aNorm,3,gl.FLOAT,false,0,0);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,g.ib);

    if(wireframeMode){{
      // draw as lines
      gl.drawElements(gl.LINES,g.count,gl.UNSIGNED_SHORT,0);
    }} else {{
      gl.drawElements(gl.TRIANGLES,g.count,gl.UNSIGNED_SHORT,0);
    }}
  }});

  // ── Draw gizmo over selected
  if(selected){{
    gl.disable(gl.DEPTH_TEST);
    gl.useProgram(lprog);
    const model=makeModel(selected.px,selected.py,selected.pz,0,0,0,
      Math.max(selected.sx,selected.sy,selected.sz)*0.8+0.5,
      Math.max(selected.sx,selected.sy,selected.sz)*0.8+0.5,
      Math.max(selected.sx,selected.sy,selected.sz)*0.8+0.5);
    mul(tmp,proj,view);mul(mvp,tmp,model);
    gl.uniformMatrix4fv(gl.getUniformLocation(lprog,'uMVP'),false,mvp);
    gizmoBufs.forEach(g=>{{
      gl.uniform3fv(gl.getUniformLocation(lprog,'uColor'),new Float32Array(g.color));
      gl.bindBuffer(gl.ARRAY_BUFFER,g.buf.buf);
      gl.enableVertexAttribArray(lpos);
      gl.vertexAttribPointer(lpos,3,gl.FLOAT,false,0,0);
      gl.drawArrays(gl.LINES,0,2);
    }});
    gl.enable(gl.DEPTH_TEST);
  }}

  requestAnimationFrame(render);
}}
render();

// ── Picking (ray-AABB)
function pick(ex,ey){{
  const nx=(ex/canvas.width)*2-1;
  const ny=-(ey/canvas.height)*2+1;
  // Unproject
  const [cx,cy,cz]=camPos();
  const aspect=canvas.width/canvas.height;
  const fov=Math.PI/3;
  const rdir=[nx*Math.tan(fov/2)*aspect, ny*Math.tan(fov/2), -1];
  // Transform ray direction by inverse view rotation
  const theta=orb.theta,phi=orb.phi;
  const rx_=Math.sin(phi)*Math.sin(theta);
  const ry_=Math.cos(phi);
  const rz_=Math.sin(phi)*Math.cos(theta);
  // Right and up vectors
  const right=[Math.cos(theta),0,-Math.sin(theta)];
  const up_=[
    -Math.cos(phi)*Math.sin(theta),
    Math.sin(phi),
    -Math.cos(phi)*Math.cos(theta)
  ];
  const fwd=[-rx_,-ry_,-rz_];
  const rd=[
    right[0]*rdir[0]+up_[0]*rdir[1]+fwd[0]*rdir[2],
    right[1]*rdir[0]+up_[1]*rdir[1]+fwd[1]*rdir[2],
    right[2]*rdir[0]+up_[2]*rdir[1]+fwd[2]*rdir[2],
  ];
  const rl=Math.sqrt(rd[0]*rd[0]+rd[1]*rd[1]+rd[2]*rd[2]);
  rd[0]/=rl;rd[1]/=rl;rd[2]/=rl;

  let best=null,bestT=1e9;
  objects.forEach(obj=>{{
    // Approx AABB around object center
    const r=Math.max(obj.sx,obj.sy,obj.sz)*0.9;
    // Ray-sphere approx
    const dx=obj.px-cx,dy=obj.py-cy,dz=obj.pz-cz;
    const tca=dx*rd[0]+dy*rd[1]+dz*rd[2];
    if(tca<0)return;
    const d2=(dx*dx+dy*dy+dz*dz)-tca*tca;
    if(d2>r*r)return;
    if(tca<bestT){{bestT=tca;best=obj;}}
  }});
  return best;
}}

// ── Gizmo axis picking (screen-space)
function pickGizmoAxis(mx,my){{
  if(!selected)return null;
  const [cx,cy,cz]=camPos();
  // Project gizmo axis endpoints to screen
  function project(px,py,pz){{
    const model=makeModel(selected.px,selected.py,selected.pz,0,0,0,
      Math.max(selected.sx,selected.sy,selected.sz)*0.8+0.5,
      Math.max(selected.sx,selected.sy,selected.sz)*0.8+0.5,
      Math.max(selected.sx,selected.sy,selected.sz)*0.8+0.5);
    // apply model
    const wx=model[0]*px+model[4]*py+model[8]*pz+model[12];
    const wy=model[1]*px+model[5]*py+model[9]*pz+model[13];
    const wz=model[2]*px+model[6]*py+model[10]*pz+model[14];
    // apply view
    const vx=view[0]*wx+view[4]*wy+view[8]*wz+view[12];
    const vy=view[1]*wx+view[5]*wy+view[9]*wz+view[13];
    const vz=view[2]*wx+view[6]*wy+view[10]*wz+view[14];
    const vw=view[3]*wx+view[7]*wy+view[11]*wz+view[15];
    // apply proj
    const clipx=proj[0]*vx+proj[4]*vy+proj[8]*vz+proj[12]*vw;
    const clipy=proj[1]*vx+proj[5]*vy+proj[9]*vz+proj[13]*vw;
    const clipw=proj[3]*vx+proj[7]*vy+proj[11]*vz+proj[15]*vw;
    const ndcx=clipx/clipw,ndcy=clipy/clipw;
    return [(ndcx+1)/2*canvas.width,(1-ndcy)/2*canvas.height];
  }}
  const scale=Math.max(selected.sx,selected.sy,selected.sz)*0.8+0.5;
  const tips={{x:project(1.8*scale,0,0),y:project(0,1.8*scale,0),z:project(0,0,1.8*scale)}};
  const orig=project(0,0,0);
  let best=null,bestD=18;
  ['x','y','z'].forEach(ax=>{{
    const tip=tips[ax];
    // point-to-segment distance
    const dx=tip[0]-orig[0],dy=tip[1]-orig[1];
    const l2=dx*dx+dy*dy;
    if(l2<1)return;
    const t=Math.max(0,Math.min(1,((mx-orig[0])*dx+(my-orig[1])*dy)/l2));
    const px2=orig[0]+t*dx,py2=orig[1]+t*dy;
    const d=Math.sqrt((mx-px2)**2+(my-py2)**2);
    if(d<bestD){{bestD=d;best=ax;}}
  }});
  return best;
}}

// ── Mouse interaction
let isOrb=false,isPan=false,isDrag=false;
let lm={{x:0,y:0}},dm={{x:0,y:0}};
let dragAxis=null,sp=null,sr=null,ss=null;

canvas.addEventListener('mousedown',e=>{{
  dm={{x:e.clientX,y:e.clientY}};
  if(selected){{
    const ax=pickGizmoAxis(e.clientX,e.clientY);
    if(ax){{
      isDrag=true;dragAxis=ax;
      sp={{x:selected.px,y:selected.py,z:selected.pz}};
      sr={{x:selected.rx,y:selected.ry,z:selected.rz}};
      ss={{x:selected.sx,y:selected.sy,z:selected.sz}};
      lm={{x:e.clientX,y:e.clientY}};return;
    }}
  }}
  if(e.button===0)isOrb=true;
  if(e.button===2)isPan=true;
  lm={{x:e.clientX,y:e.clientY}};
}});

canvas.addEventListener('mouseup',e=>{{
  if(isDrag){{isDrag=false;dragAxis=null;showDims(selected);return;}}
  isOrb=false;isPan=false;
  if(Math.abs(e.clientX-dm.x)<5&&Math.abs(e.clientY-dm.y)<5&&e.button===0){{
    selectObj(pick(e.clientX,e.clientY));
  }}
}});

canvas.addEventListener('mousemove',e=>{{
  if(isDrag&&selected&&dragAxis){{
    const dx=(e.clientX-lm.x)*0.02,dy=-(e.clientY-lm.y)*0.02;
    const d=Math.abs(dx)>Math.abs(dy)?dx:dy;
    if(transformMode==='move'){{
      if(dragAxis==='x')selected.px=snap(sp.x+dx*2.5);
      if(dragAxis==='y')selected.py=snap(sp.y+dy*2.5);
      if(dragAxis==='z')selected.pz=snap(sp.z+dx*2.5);
    }}else if(transformMode==='rotate'){{
      if(dragAxis==='x')selected.rx=sr.x+d*3;
      if(dragAxis==='y')selected.ry=sr.y+d*3;
      if(dragAxis==='z')selected.rz=sr.z+d*3;
    }}else if(transformMode==='scale'){{
      const f=1+d*1.5;
      if(dragAxis==='x')selected.sx=Math.max(0.05,ss.x*f);
      if(dragAxis==='y')selected.sy=Math.max(0.05,ss.y*f);
      if(dragAxis==='z')selected.sz=Math.max(0.05,ss.z*f);
    }}
    lm={{x:e.clientX,y:e.clientY}};return;
  }}
  if(isOrb){{
    orb.theta-=(e.clientX-lm.x)*0.007;
    orb.phi-=(e.clientY-lm.y)*0.007;
    orb.phi=Math.max(0.08,Math.min(Math.PI-0.08,orb.phi));
  }}
  if(isPan){{
    const spd=0.012*(orb.r/10);
    const right=[Math.cos(orb.theta),0,-Math.sin(orb.theta)];
    orb.tx-=right[0]*(e.clientX-lm.x)*spd;
    orb.tz-=right[2]*(e.clientX-lm.x)*spd;
    orb.ty+=(e.clientY-lm.y)*spd;
  }}
  lm={{x:e.clientX,y:e.clientY}};
}});
canvas.addEventListener('wheel',e=>{{
  orb.r*=1+e.deltaY*0.001;orb.r=Math.max(2,Math.min(80,orb.r));
}},{{passive:true}});
canvas.addEventListener('contextmenu',e=>e.preventDefault());

// ── AI
function closeAI(){{document.getElementById('ai-panel').style.display='none';}}
function triggerAnalyze(){{
  if(!selected)return setStatus('Select an object first');
  const panel=document.getElementById('ai-panel');
  const body=document.getElementById('ai-body');
  panel.style.display='flex';
  body.innerHTML='<div class="loading">Sending to AI...</div>';
  setStatus('Sending to AI...');
  const col=selected.color;
  const obj={{
    name:selected.name,type:selected.type,
    position:[+selected.px.toFixed(3),+selected.py.toFixed(3),+selected.pz.toFixed(3)],
    rotation:[+selected.rx.toFixed(3),+selected.ry.toFixed(3),+selected.rz.toFixed(3)],
    scale:[+selected.sx.toFixed(3),+selected.sy.toFixed(3),+selected.sz.toFixed(3)],
    color:rgbToHex(col[0],col[1],col[2]),total:objects.length
  }};
  const encoded=encodeURIComponent(JSON.stringify(obj));
  const url=new URL(window.parent.location.href);
  url.searchParams.set('analyze',encoded);
  window.parent.location.href=url.toString();
}}

// Show previous AI result
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
      const paras=result.split('\\n').filter(l=>l.trim()).map(l=>'<div class="ap">'+l+'</div>').join('');
      body.innerHTML='<div class="otag">'+obj.name+' · '+obj.type+'</div>'+paras;
    }}
  }}catch(e){{body.innerHTML='<div class="ap">'+result+'</div>';}}
}})();

document.addEventListener('keydown',e=>{{
  const t=document.activeElement.tagName;
  if(t==='INPUT'||t==='TEXTAREA')return;
  if(e.key.toLowerCase()==='x')triggerAnalyze();
  if(e.key==='Escape')closeAI();
  if(e.key==='Delete')deleteSelected();
}});

function setStatus(msg){{document.getElementById('status').innerText=msg;}}

// ── Sidebar commands
(function(){{
  const cmd={js_cmd};
  if(!cmd||cmd==='null')return;
  if(cmd.startsWith('add:')){{addShape(cmd.split(':')[1]);return;}}
  if(cmd.startsWith('cad:')){{cadOp(cmd.split(':')[1]);return;}}
  if(cmd==='delete'){{deleteSelected();return;}}
  if(cmd==='clear'){{clearScene();return;}}
  if(cmd.startsWith('color:')){{setColor(cmd.split(':')[1]);return;}}
  if(cmd.startsWith('pos:')){{const v=cmd.slice(4).split(',');applyPos(v[0],v[1],v[2]);return;}}
  if(cmd.startsWith('scale:')){{const v=cmd.slice(6).split(',');applyScaleFn(v[0],v[1],v[2]);return;}}
}})();
</script></body></html>"""

st.markdown("## 🔩 CAD AI Studio")
components.html(HTML, height=700, scrolling=False)
st.caption("Click shape · select · drag red/green/blue arrows · **X** to AI-analyze | Secrets: OPENAI_API_KEY")
'''

with open('/mnt/user-data/outputs/ai_design_studio/app.py', 'w') as f:
    f.write(code)
print("Written", len(code), "chars")