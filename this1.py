import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Mini CAD", layout="wide")

st.title("🛠️ Mini CAD Prototype")

# -----------------------
# Create Figure
# -----------------------

fig = go.Figure()

objects = []

# -----------------------
# Ground Plane
# -----------------------

x = np.linspace(-10, 10, 2)
y = np.linspace(-10, 10, 2)

X, Y = np.meshgrid(x, y)
Z = np.zeros_like(X)

objects.append(
    go.Surface(
        x=X,
        y=Y,
        z=Z,
        colorscale=[[0, "#DDDDDD"], [1, "#DDDDDD"]],
        showscale=False,
        opacity=0.8,
        name="Ground"
    )
)

# -----------------------
# Triangle
# -----------------------

objects.append(
    go.Mesh3d(
        x=[2, 5, 3.5],
        y=[2, 2, 5],
        z=[0, 0, 3],
        color="red",
        opacity=0.8,
        name="Triangle"
    )
)

# -----------------------
# Rectangle
# -----------------------

objects.append(
    go.Surface(
        x=[[ -6, -2],
           [ -6, -2]],

        y=[[2, 2],
           [6, 6]],

        z=[[1, 1],
           [1, 1]],

        colorscale=[[0, "blue"], [1, "blue"]],
        showscale=False,
        opacity=0.8,
        name="Rectangle"
    )
)

# -----------------------
# Add all objects
# -----------------------

for obj in objects:
    fig.add_trace(obj)

# -----------------------
# X Axis
# -----------------------

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

# -----------------------
# Y Axis
# -----------------------

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

# -----------------------
# Z Axis
# -----------------------

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

# -----------------------
# Layout
# -----------------------

fig.update_layout(

    scene=dict(

        xaxis=dict(
            range=[-10, 10],
            backgroundcolor="white"
        ),

        yaxis=dict(
            range=[-10, 10],
            backgroundcolor="white"
        ),

        zaxis=dict(
            range=[-10, 10],
            backgroundcolor="white"
        ),

        aspectmode="cube",
    ),

    margin=dict(
        l=0,
        r=0,
        t=40,
        b=0
    ),

    height=750,

    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)
