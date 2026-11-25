import streamlit as st
import numpy as np
from PIL import Image
import plotly.graph_objects as go
import serial
import time
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

st.set_page_config(layout="wide")

st.title("Quantum-Inspired Image Processing")
st.subheader("2D to 3D Conversion with Arduino")

# Arduino section
st.sidebar.header("Arduino Distance Control")

port = st.sidebar.text_input("COM Port", "COM3")

if "distance" not in st.session_state:
    st.session_state.distance = 20.0

if st.sidebar.button("Read Distance"):

    arduino = serial.Serial(port, 9600, timeout=2)
    time.sleep(2)

    reading = None

    for i in range(10):
        data = arduino.readline().decode(
            "utf-8", errors="replace"
        ).strip()

        if data.startswith("Distance:"):
            reading = float(
                data.split(":")[1].replace("cm", "").strip()
            )
            break

    arduino.close()

    if reading is not None:
        st.session_state.distance = reading
        st.sidebar.success("Reading received!")
    else:
        st.sidebar.warning("No distance reading received.")

distance = st.session_state.distance

st.sidebar.metric("Distance", f"{distance:.2f} cm")

height_scale = np.interp(
    np.clip(distance, 5, 100),
    [5, 100],
    [2.0, 0.5]
)

st.sidebar.metric("3D Height Scale", f"{height_scale:.2f}x")

# Image upload
uploaded = st.file_uploader(
    "Upload a 2D image",
    type=["jpg", "jpeg", "png"]
)

if uploaded is not None:

    image = Image.open(uploaded)
    gray = image.convert("L").resize((64, 64))

    pixels = np.array(gray)
    normalized = pixels / 255.0

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Original Image")

    with col2:
        st.image(gray, caption="Grayscale Image")

    # Quantum simulation
    st.header("Quantum Circuit Simulation")

    pixel = st.slider("Pixel Intensity", 0, 255, 128)

    p = pixel / 255.0
    theta = 2 * np.arcsin(np.sqrt(p))

    circuit = QuantumCircuit(1)
    circuit.ry(float(theta), 0)

    state = Statevector.from_instruction(circuit)
    probabilities = state.probabilities()

    st.write("Quantum Circuit:")
    st.code(str(circuit.draw(output="text")))

    st.write("Probability of |0>:", float(probabilities[0]))
    st.write("Probability of |1>:", float(probabilities[1]))

    # 3D visualization
    st.header("Arduino Controlled 3D Image")

    z = normalized * height_scale

    fig = go.Figure(
        data=[
            go.Surface(
                z=z,
                colorscale="Viridis"
            )
        ]
    )

    fig.update_layout(
        height=600,
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Height"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    st.success("Project running successfully!")

else:
    st.info("Upload an image to begin.")