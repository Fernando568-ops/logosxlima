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

# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("Shapes")

if st.sidebar.button("Add Plane"):
    st.session_state.objects.append({
        "type": "Plane",
        "x":0,
        "y":0,
        "z":0
    })

if st.sidebar.button("Add Triangle"):
    st.session_state.objects.append({
        "type": "Triangle",
        "x":0,
        "y":0,
        "z":0
    })

if st.sidebar.button("Add Rectangle"):
    st.session_state.objects.append({
        "type": "Rectangle",
        "x":0,
        "y":0,
        "z":0
    })

if st.sidebar.button("Add Cube"):
    st.session_state.objects.append({
        "type": "Cube",
        "x":0,
        "y":0,
        "z":0
    })

if st.sidebar.button("Add Sphere"):
    st.session_state.objects.append({
        "type": "Sphere",
        "x":0,
        "y":0,
        "z":0
    })

if st.sidebar.button("Add Cylinder"):
    st.session_state.objects.append({
        "type": "Cylinder",
        "x":0,
        "y":0,
        "z":0
    })

if st.sidebar.button("Add Cone"):
    st.session_state.objects.append({
        "type": "Cone",
        "x":0,
        "y":0,
        "z":0
    })

# -----------------------------
# Figure
# -----------------------------

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

for shape, index in st.session_state.objects:

    offset = index * 3

    if shape == "plane":

        x = np.linspace(-1,1,2) + offset
        y = np.linspace(-1,1,2)

        X,Y = np.meshgrid(x,y)
        Z = np.zeros_like(X)

        fig.add_trace(go.Surface(
            x=X,
            y=Y,
            z=Z,
            showscale=False,
            opacity=0.8,
            colorscale=[[0,"lightgray"],[1,"lightgray"]]
        ))

    elif shape == "triangle":

        fig.add_trace(go.Mesh3d(

            x=[0+offset,2+offset,1+offset],
            y=[0,0,2],
            z=[0,0,2],

            color="red",
            opacity=.8
        ))

    elif shape == "rectangle":

        fig.add_trace(go.Surface(

            x=[[0+offset,2+offset],
               [0+offset,2+offset]],

            y=[[0,0],
               [2,2]],

            z=[[1,1],
               [1,1]],

            colorscale=[[0,"blue"],[1,"blue"]],
            showscale=False,
            opacity=.8
        ))

    elif shape == "cube":

        x0 = offset
    
        vertices = np.array([
            [0+x0,0,0],
            [1+x0,0,0],
            [1+x0,1,0],
            [0+x0,1,0],
            [0+x0,0,1],
            [1+x0,0,1],
            [1+x0,1,1],
            [0+x0,1,1]
        ])
    
        edges = [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7)
        ]
    
        for e in edges:
    
            fig.add_trace(
                go.Scatter3d(
    
                    x=[vertices[e[0]][0],vertices[e[1]][0]],
                    y=[vertices[e[0]][1],vertices[e[1]][1]],
                    z=[vertices[e[0]][2],vertices[e[1]][2]],
    
                    mode="lines",
    
                    line=dict(width=6,color="black"),
    
                    showlegend=False
                )
            )

    elif shape == "sphere":

        u = np.linspace(0,2*np.pi,40)
        v = np.linspace(0,np.pi,20)
    
        x = np.outer(np.cos(u),np.sin(v)) + offset
        y = np.outer(np.sin(u),np.sin(v))
        z = np.outer(np.ones(np.size(u)),np.cos(v))
    
        fig.add_trace(
            go.Surface(
                x=x,
                y=y,
                z=z,
                opacity=.8,
                colorscale="Viridis",
                showscale=False
            )
        )

    elif shape == "cylinder":

        theta = np.linspace(0,2*np.pi,40)
        z = np.linspace(0,2,20)
    
        theta,z = np.meshgrid(theta,z)
    
        x = np.cos(theta)+offset
        y = np.sin(theta)
    
        fig.add_trace(
            go.Surface(
                x=x,
                y=y,
                z=z,
                opacity=.8,
                colorscale="Blues",
                showscale=False
            )
        )

    elif shape == "cone":

        theta = np.linspace(0,2*np.pi,40)
        h = np.linspace(0,2,20)
    
        theta,h = np.meshgrid(theta,h)
    
        r = 1-h/2
    
        x = r*np.cos(theta)+offset
        y = r*np.sin(theta)
        z = h
    
        fig.add_trace(
            go.Surface(
                x=x,
                y=y,
                z=z,
                opacity=.8,
                colorscale="Reds",
                showscale=False
            )
        )

# -----------------------------
# Layout
# -----------------------------

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
