import streamlit as st
import numpy as np
import requests
import os
import json
import plotly.graph_objects as go
from skyfield.api import load, EarthSatellite
from datetime import datetime, timedelta, UTC

st.set_page_config(
    page_title="Orbital Collision Avoidance",
    layout="wide"
)

st.title("Orbital Collision Avoidance")
st.write("V0.4 - Visualizing Satellite Orbit Around Earth (Error handling)")

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "satellite_cache.json")
CELESTRAK_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"


def fetch_catalog():
    response = requests.get(CELESTRAK_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    response.raise_for_status()

    lines = [line.strip() for line in response.text.strip().splitlines() if line.strip()]
    catalog = {}
    
    for i in range(0, len(lines) - 2, 3):
        name = lines[i]
        line1 = lines[i + 1]
        line2 = lines[i + 2]
        norad_id = line1[2:7].strip()
        catalog[f"{name} ({norad_id})"] = (name, line1, line2)

    return catalog


refresh_select = st.sidebar.button("Refresh from Celestrak")
download_req = refresh_select or not os.path.exists(CACHE_FILE)

catalog = None
if download_req:
    try:
        catalog = fetch_catalog()
        with open(CACHE_FILE, "w") as f:
            json.dump(catalog, f)

    except requests.exceptions.Timeout:
        st.warning("Too long to respond")

    except requests.exceptions.ConnectionError:
        st.warning("Couldn't connect")

    except requests.exceptions.HTTPError as e:
        st.warning(f"Error")

if catalog is None:
    if os.path.exists(CACHE_FILE):
        st.info("Using last saved satellite")
        with open(CACHE_FILE, "r") as f:
            catalog = json.load(f)
    else:
        st.error("No satellite data available")
        st.stop()

catalog = {k: tuple(v) for k, v in catalog.items()}

labels = sorted(catalog.keys())

default_index = 0
for i, label in enumerate(labels):
    if label.startswith("ISS "):
        default_index = i
        break

selected_label = st.selectbox(
    "Search for a satellite",
    options=labels,
    index=default_index
)

name, line, line2 = catalog[selected_label]
st.success(f"Satellite Found")



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