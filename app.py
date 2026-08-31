import streamlit as st
import numpy as np
import plotly.graph_objects as go
from skyfield.api import load, EarthSatellite
from datetime import datetime, timedelta, UTC

st.set_page_config(
    page_title="Orbital Collision Avoidance",
    layout="wide"
)

st.title("Orbital Collision Avoidance")
st.write("V0.1 - Visualizing Satellite Orbit Around Earth")

name ="ISS (ZARYA)"
line = "1 25544U 98067A   24171.51041667  .00016717  00000+0  10270-3 0  9003"
line2 = "2 25544  51.6416 280.2231 0006703 130.5360 325.0288 15.50000000  1234"

duration_hours = st.slider(
    "Hours Orbit Visualized For",
    min_value=0.25,
    max_value=24.0,
    value=3.0,
    step=0.25
)

num_points = st.slider(
    "Number of orbit points (calculations)",
    100,
    2000,
    500,
)

ts = load.timescale()

satellite = EarthSatellite(
    line,
    line2,
    name,
    ts
)

current_time = datetime.now(UTC)

time_list = [
    current_time + timedelta(hours=i * duration_hours / (num_points - 1))
    for i in range(num_points)
]

times = ts.from_datetimes(time_list)
geo_pos = satellite.at(times)
x,y,z = geo_pos.position.km

EARTH_RAD = 6371
u = np.linspace(0, 2 * np.pi, 80)
v = np.linspace(0, np.pi, 40)
earth_x = EARTH_RAD*np.outer(np.cos(u), np.sin(v))
earth_y = EARTH_RAD*np.outer(np.sin(u), np.sin(v))
earth_z = EARTH_RAD*np.outer(np.ones_like(u), np.cos(v))

figure = go.Figure()
figure.add_trace(
    go.Surface(
        x=earth_x,
        y = earth_y,
        z = earth_z,
        opacity = 0.6,
        showscale = False,
        name = "Earth"
    )
)

figure.add_trace(
    go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode = "lines",
        line = dict(width=4),
        name="Orbit"
    )
)

figure.add_trace(
    go.Scatter3d(
        x=[x[0]],
        y=[y[0]],
        z=[z[0]],
        mode="markers",
        marker=dict(size=6),
        name="Start Position"

    )
)

figure.add_trace(
    go.Scatter3d(
        x=[x[-1]],
        y=[y[-1]],
        z=[z[-1]],
        mode="markers",
        marker=dict(size=8),
        name="End Position"
    )
)

figure.update_layout(
    scene=dict(
        xaxis_title="X (km)",
        yaxis_title="Y (km)",
        zaxis_title="Z (km)",
        aspectmode="data"
    ),
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=30
    )

)

st.plotly_chart(
    figure,
    use_container_width=True

)


st.subheader("Simulation Information")
st.write(f"Satellite: {name}")
st.write(f"Simulation Length: {duration_hours} hours")
st.write(f"Calculated Positions: {num_points}")
