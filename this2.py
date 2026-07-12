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
    st.session_state.objects.append(("plane", len(st.session_state.objects)))

if st.sidebar.button("Add Triangle"):
    st.session_state.objects.append(("triangle", len(st.session_state.objects)))

if st.sidebar.button("Add Rectangle"):
    st.session_state.objects.append(("rectangle", len(st.session_state.objects)))

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
