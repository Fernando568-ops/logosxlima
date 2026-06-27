import streamlit as st
import requests

# =========================
# PAGE
# =========================
st.set_page_config(
    page_title="Engineering 3D AI Analyzer",
    layout="wide"
)

st.title("🛠️ Engineering 3D AI Analyzer")

# =========================
# API KEY INPUT
# =========================
api_key = st.text_input(
    "OpenRouter API Key",
    type="password"
)

# =========================
# FILE UPLOAD
# =========================
uploaded_file = st.file_uploader(
    "Upload 3D Model",
    type=["obj", "stl"]
)

# =========================
# AI FUNCTION
# =========================
def analyze_with_ai(prompt, api_key):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            timeout=60
        )

        data = response.json()

        if response.status_code != 200:
            return f"API Error:\n{data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error:\n{e}"


# =========================
# MODEL ANALYSIS
# =========================
if uploaded_file is not None:

    file_bytes = uploaded_file.read()

    file_text = file_bytes.decode(
        "utf-8",
        errors="ignore"
    )

    lines = file_text.splitlines()

    vertices = sum(
        1 for line in lines
        if line.startswith("v ")
    )

    faces = sum(
        1 for line in lines
        if line.startswith("f ")
    )

    file_size = len(file_bytes) / 1024

    if faces < 1000:
        complexity = "Low"
    elif faces < 10000:
        complexity = "Medium"
    else:
        complexity = "High"

    st.subheader("📊 Engineering Metrics")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Vertices", vertices)
    c2.metric("Faces", faces)
    c3.metric("Complexity", complexity)
    c4.metric("Size (KB)", f"{file_size:.2f}")

    density = 0

    if vertices > 0:
        density = faces / vertices

    st.metric(
        "Triangle Density",
        f"{density:.2f}"
    )

    # =========================
    # AI BUTTON (X)
    # =========================
    if st.button("X"):

        if api_key.strip() == "":
            st.error("Please enter an API Key.")

        else:

            prompt = f"""
You are a professional mechanical and CAD engineer.

Analyze this 3D model.

Vertices: {vertices}
Faces: {faces}
Complexity: {complexity}
Triangle Density: {density:.2f}
File Size: {file_size:.2f} KB

Provide:

1. Engineering Summary
2. Geometry Assessment
3. Manufacturability
4. Structural Concerns
5. Performance Considerations
6. Optimization Suggestions
7. Recommended Applications
8. Estimated Modelling Quality
"""

            with st.spinner("Running Engineering AI Analysis..."):

                result = analyze_with_ai(
                    prompt,
                    api_key
                )

            st.subheader("🤖 AI Engineering Report")

            st.text_area(
                "Analysis",
                result,
                height=500
            )