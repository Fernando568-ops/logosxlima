import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")

st.title("Mini CAD")

# -----------------------------
# Store shapes between reruns
# -----------------------------

if "objects" not in st.session_state:
    st.session_state.objects = []

if "history" not in st.session_state:
    st.session_state.history = []

if "selected" not in st.session_state:
    st.session_state.selected = None

# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("Shapes")

if st.session_state.selected is not None:

    obj = st.session_state.objects[st.session_state.selected]

    st.sidebar.success(f"Selected: {obj['type']}")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Move")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("⬅ Left"):
            st.session_state.objects[st.session_state.selected]["x"] -= 1

            st.session_state.history.append({

                "operation":"Move",
        
                "axis":"X",
        
                "amount":-1

    })
    
    with col2:
        if st.button("Right ➡"):
            st.session_state.objects[st.session_state.selected]["x"] += 1

            st.session_state.history.append({

                "operation":"Move",
        
                "axis":"X",
        
                "amount":1

    })

if "extrude_height" not in st.session_state:
    st.session_state.extrude_height = 2.0

if st.sidebar.button("Add Plane"):
    st.session_state.objects.append({
        "type": "Plane",
        "x":0,
        "y":0,
        "z":0
    })

    st.session_state.history.append({

    "operation":"Add Object",

    "type":"Plane"

    })

if st.sidebar.button("Add Triangle"):
    st.session_state.objects.append({
        "type": "Triangle",
        "x":0,
        "y":0,
        "z":0
    })
    st.session_state.history.append({

    "operation":"Add Object",

    "type":"Triangle"

    })

if st.sidebar.button("Add Rectangle"):
    st.session_state.objects.append({
        "type": "Rectangle",
        "x":0,
        "y":0,
        "z":0
    })
    st.session_state.history.append({

    "operation":"Add Object",

    "type":"Rectangle"

    })

if st.sidebar.button("Add Cube"):
    st.session_state.objects.append({
        "type": "Cube",
        "x":0,
        "y":0,
        "z":0,
    })
    st.session_state.history.append({

    "operation":"Add Object",

    "type":"Cube"

    })

if st.sidebar.button("Add Sphere"):
    st.session_state.objects.append({
        "type": "Sphere",
        "x":0,
        "y":0,
        "z":0
    })
    st.session_state.history.append({

    "operation":"Add Object",

    "type":"Sphere"

    })

if st.sidebar.button("Add Cylinder"):
    st.session_state.objects.append({
        "type": "Cylinder",
        "x":0,
        "y":0,
        "z":0
    })
    st.session_state.history.append({

    "operation":"Add Object",

    "type":"Cylinder"

    })

if st.sidebar.button("Add Cone"):
    st.session_state.objects.append({
        "type": "Cone",
        "x":0,
        "y":0,
        "z":0
    })
    st.session_state.history.append({

    "operation":"Add Object",

    "type":"Cone"

    })

# -----------------------------
# Draw Custom Shape
# -----------------------------

st.sidebar.markdown("---")
st.sidebar.subheader("Draw Shape")

if "points" not in st.session_state:
    st.session_state.points = []

x = st.sidebar.number_input("X", value=0.0, step=1.0)
y = st.sidebar.number_input("Y", value=0.0, step=1.0)

if st.sidebar.button("Add Point"):

    st.session_state.points.append((x, y))

    st.session_state.history.append({
        "operation": "Add Point",
        "x": x,
        "y": y
    })

if st.sidebar.button("Clear Points"):

    st.session_state.points = []

st.sidebar.subheader("Extrusion")

height = st.sidebar.slider(
    "Height",
    min_value=0.5,
    max_value=10.0,
    value=2.0,
    step=0.5
)

if st.sidebar.button("Extrude"):
    st.session_state.extrude = True
    st.session_state.extrude_height = height

    st.session_state.history.append({

        "operation": "Extrude",

        "height": height

    })

if "extrude" not in st.session_state:
        st.session_state.extrude = False

if len(st.session_state.points) >= 2:

        xs = [p[0] for p in st.session_state.points]
        ys = [p[1] for p in st.session_state.points]
    
        xs.append(xs[0])
        ys.append(ys[0])


st.sidebar.write("Current Points")

for i, p in enumerate(st.session_state.points):

    st.sidebar.write(f"{i+1}. ({p[0]}, {p[1]})")

st.sidebar.markdown("---")
st.sidebar.subheader("Objects")

st.sidebar.markdown("---")
st.sidebar.subheader("History")

for i, action in enumerate(st.session_state.history):

    st.sidebar.write(f"{i+1}. {action}")

for i, obj in enumerate(st.session_state.objects):

    if st.sidebar.button(f"Select {obj['type']} {i+1}"):

        st.session_state.selected = i
# -----------------------------
# Figure
#------------------------------

st.sidebar.markdown("---")
st.sidebar.subheader("Command Console")

with st.sidebar.form("command_form"):

    command = st.text_input("Command")

    submitted = st.form_submit_button("Run Command")

if submitted:

    command = command.strip().upper()

    if command == "ADD CUBE":

        st.session_state.objects.append({
            "type": "Cube",
            "x": 0,
            "y": 0,
            "z": 0
        })

        st.session_state.history.append({
            "operation": "Command",
            "command": command
        })

        st.rerun()

    else:

        st.sidebar.error("Unknown command.")

fig = go.Figure()

# Axes

fig.add_trace(go.Scatter3d(
    x=[0,10], y=[0,0], z=[0,0],
    mode="lines",
    line=dict(color="red", width=8),
    showlegend=False))

fig.add_trace(go.Scatter3d(
    x=[0,0], y=[0,10], z=[0,0],
    mode="lines",
    line=dict(color="green", width=8),
    showlegend=False))

fig.add_trace(go.Scatter3d(
    x=[0,0], y=[0,0], z=[0,10],
    mode="lines",
    line=dict(color="blue", width=8),
    showlegend=False))

# -----------------------------
# Draw every object
# -----------------------------
# -----------------------------
# Draw every object
# -----------------------------

for obj in st.session_state.objects:

    shape = obj["type"]
    x0 = obj["x"]
    y0 = obj["y"]
    z0 = obj["z"]

    # -------------------------
    # Plane
    # -------------------------

    if shape == "Plane":

        x = np.linspace(-1, 1, 2) + x0
        y = np.linspace(-1, 1, 2) + y0

        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X) + z0

        fig.add_trace(
            go.Surface(
                x=X,
                y=Y,
                z=Z,
                showscale=False,
                opacity=0.8,
                colorscale=[[0, "lightgray"], [1, "lightgray"]]
            )
        )

    # -------------------------
    # Triangle
    # -------------------------

    elif shape == "Triangle":

        fig.add_trace(
            go.Mesh3d(
                x=[0+x0, 2+x0, 1+x0],
                y=[0+y0, 0+y0, 2+y0],
                z=[0+z0, 0+z0, 2+z0],

                color="red",
                opacity=0.8
            )
        )

    # -------------------------
    # Rectangle
    # -------------------------

    elif shape == "Rectangle":

        fig.add_trace(
            go.Surface(
                x=[
                    [0+x0, 2+x0],
                    [0+x0, 2+x0]
                ],

                y=[
                    [0+y0, 0+y0],
                    [2+y0, 2+y0]
                ],

                z=[
                    [1+z0, 1+z0],
                    [1+z0, 1+z0]
                ],

                colorscale=[[0, "blue"], [1, "blue"]],
                showscale=False,
                opacity=0.8
            )
        )

    # -------------------------
    # Cube
    # -------------------------

    elif shape == "Cube":

        vertices = np.array([
            [0+x0, 0+y0, 0+z0],
            [1+x0, 0+y0, 0+z0],
            [1+x0, 1+y0, 0+z0],
            [0+x0, 1+y0, 0+z0],
            [0+x0, 0+y0, 1+z0],
            [1+x0, 0+y0, 1+z0],
            [1+x0, 1+y0, 1+z0],
            [0+x0, 1+y0, 1+z0]
        ])

        edges = [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7)
        ]

        for e in edges:

            fig.add_trace(
                go.Scatter3d(
                    x=[vertices[e[0]][0], vertices[e[1]][0]],
                    y=[vertices[e[0]][1], vertices[e[1]][1]],
                    z=[vertices[e[0]][2], vertices[e[1]][2]],
                    mode="lines",
                    line=dict(width=6, color="black"),
                    showlegend=False
                )
            )

    # -------------------------
    # Sphere
    # -------------------------

    elif shape == "Sphere":

        u = np.linspace(0, 2*np.pi, 40)
        v = np.linspace(0, np.pi, 20)

        x = np.outer(np.cos(u), np.sin(v)) + x0
        y = np.outer(np.sin(u), np.sin(v)) + y0
        z = np.outer(np.ones(np.size(u)), np.cos(v)) + z0

        fig.add_trace(
            go.Surface(
                x=x,
                y=y,
                z=z,
                opacity=0.8,
                colorscale="Viridis",
                showscale=False
            )
        )

    # -------------------------
    # Cylinder
    # -------------------------

    elif shape == "Cylinder":

        theta = np.linspace(0, 2*np.pi, 40)
        z = np.linspace(0, 2, 20)

        theta, z = np.meshgrid(theta, z)

        x = np.cos(theta) + x0
        y = np.sin(theta) + y0
        z = z + z0

        fig.add_trace(
            go.Surface(
                x=x,
                y=y,
                z=z,
                opacity=0.8,
                colorscale="Blues",
                showscale=False
            )
        )

    # -------------------------
    # Cone
    # -------------------------

    elif shape == "Cone":

        theta = np.linspace(0, 2*np.pi, 40)
        h = np.linspace(0, 2, 20)

        theta, h = np.meshgrid(theta, h)

        r = 1 - h/2

        x = r*np.cos(theta) + x0
        y = r*np.sin(theta) + y0
        z = h + z0

        fig.add_trace(
            go.Surface(
                x=x,
                y=y,
                z=z,
                opacity=0.8,
                colorscale="Reds",
                showscale=False
            )
        )
# -----------------------------
# Layout
# -----------------------------
# -----------------------------
# Draw Custom Polygon
# -----------------------------

# -----------------------------
# Command Console
# -----------------------------

if len(st.session_state.points) >= 2:

    pts = st.session_state.points

    height = 2

    # Bottom
    xb = [p[0] for p in pts]
    yb = [p[1] for p in pts]
    zb = [0,0,0,0]

    # Top
    xt = xb
    yt = yb
    zt = [height]*4


    # Draw sketch if not extruded

    if not st.session_state.extrude:

        fig.add_trace(
            go.Scatter3d(

                x=xb+[xb[0]],
                y=yb+[yb[0]],
                z=zb+[0],

                mode="lines+markers",

                line=dict(width=5),

                marker=dict(size=5)
            )
        )

    else:

        # Bottom face

        fig.add_trace(go.Mesh3d(
            x=xb,
            y=yb,
            z=zb,

            color="lightblue",
            opacity=0.5
        ))

        # Top face

        fig.add_trace(go.Mesh3d(
            x=xt,
            y=yt,
            z=zt,

            color="lightblue",
            opacity=0.5
        ))

        # Vertical edges

        for i in range(len(xb)):
            
            fig.add_trace(

                go.Scatter3d(

                    x=[xb[i],xt[i]],
                    y=[yb[i],yt[i]],
                    z=[0,height],

                    mode="lines",

                    line=dict(width=6,color="black"),

                    showlegend=False
                )

            )

fig.update_layout(

scene=dict(

xaxis=dict(range=[-5,20]),
yaxis=dict(range=[-5,20]),
zaxis=dict(range=[-5,20]),

aspectmode="cube"

),

height=700,

margin=dict(l=0,r=0,b=0,t=30)

)

st.plotly_chart(fig,use_container_width=True)
