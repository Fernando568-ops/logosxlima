import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Simple 3D Plane", layout="wide")

st.title("🛠️ Simple Draggable 3D Plane")
3
# Create a square plane
x = np.linspace(-10, 10, 2)
y = np.linspace(-10, 10, 2)

X, Y = np.meshgrid(x, y)
Z = np.zeros_like(X)

fig = go.Figure()

# Plane
fig.add_trace(
    go.Surface(
        x=X,
        y=Y,
        z=Z,
        colorscale=[[0, "#D3D3D3"], [1, "#D3D3D3"]],
        showscale=False,
        opacity=0.9,
    )
)

# X-axis (Red)
fig.add_trace(
    go.Scatter3d(
        x=[0, 10],
        y=[0, 0],
        z=[0, 0],
        mode="lines",
        line=dict(color="red", width=8),
        name="X"
    )
)

# Y-axis (Green)
fig.add_trace(
    go.Scatter3d(
        x=[0, 0],
        y=[0, 10],
        z=[0, 0],
        mode="lines",
        line=dict(color="green", width=8),
        name="Y"
    )
)

# Z-axis (Blue)
fig.add_trace(
    go.Scatter3d(
        x=[0, 0],
        y=[0, 0],
        z=[0, 10],
        mode="lines",
        line=dict(color="blue", width=8),
        name="Z"
    )
)

fig.update_layout(
    scene=dict(
        xaxis=dict(range=[-10, 10]),
        yaxis=dict(range=[-10, 10]),
        zaxis=dict(range=[-10, 10]),
        aspectmode="cube",
    ),
    margin=dict(l=0, r=0, t=30, b=0),
    height=700,
)

st.plotly_chart(fig, use_container_width=True)