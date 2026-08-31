import streamlit as st
import numpy as np
import requests
import plotly.graph_objects as go
from skyfield.api import load, EarthSatellite
from datetime import datetime, timedelta, UTC

st.set_page_config(
    page_title="Orbital Collision Avoidance",
    layout="wide"
)

st.title("Orbital Collision Avoidance")
st.write("V0.2 - Visualizing Satellite Orbit Around Earth (NORAD/name search)")

satellite_query = st.text_input(
    "Enter the name of a satellite or its NORAD catalog number",
    value = "ISS"
)

def get_satellite(query):
    query = query.strip()
    if not query:
        return None
    if query.isdigit():
        url = ("https://celestrak.org/NORAD/elements/gp.php"
            f"?CATNR={query}&FORMAT=TLE"
        )
    else:
        url = ("https://celestrak.org/NORAD/elements/gp.php"
            f"?NAME={query}&FORMAT=TLE")
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        return None
    
    lines = response.text.strip().splitlines()

    lines = [line.strip() for line in lines if line.strip()]

    if len(lines) < 3:
        return None
    
    satellite_name = lines[0]
    tle_line1 = lines[1]
    tle_line2 = lines[2]
    
    return satellite_name, tle_line1, tle_line2

satellite_data = get_satellite(satellite_query)

if satellite_data is None:
    st.error("Satellite not found. Try another.")
    st.stop()

name, line, line2 = satellite_data

st.success(f"Found {name}")

duration_hours = st.slider(
    "Hours Orbit Visualized For",
    min_value=0.0,
    max_value=24.0,
    value=0.0,
    step=0.25
)

num_points = st.slider(
    "Number of orbit points (calculations)",
    100,
    2000,
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

if duration_hours == 0:
    max_val = 24.0
else:
    max_val = duration_hours
st.subheader("Satellite Position")
pos = st.slider(
    "Move satellite through orbit (in orbit points)",
    min_value=0,
    max_value = num_points,
    value=0
)

cur_x = x[pos]
cur_y = y[pos]
cur_z = z[pos]
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
        x=[cur_x],
        y = [cur_y],
        z = [cur_z],
        mode = "markers",
        marker = dict(
            size = 8
        ),
        name = "Current Position"
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
st.write("Current Position")
st.write(f"X: {cur_x:.2f} km")
st.write(f"Y: {cur_y:.2f} km")
st.write(f"Z: {cur_z:.2f} km")