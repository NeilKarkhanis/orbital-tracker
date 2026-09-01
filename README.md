# Orbital Tracker

A Streamlit app for visualizing various satellite orbits around the Earth in three dimensions. Search for any satellite using its name or NORAD ID using the dropdown menu, then see its orbital path plotted using real orbital data. 

## Features

- **Live satellite catalog search** — Dropdown menu covering all the active satellites currently tracked by Celestrak, with live filtering as letters are typed
- **3D orbit visualization** — plots the satellite's path around the Earth using [Plotly](https://plotly.com/python/3d-charts/), with adjustable time windows and numbers of positional calculations
- **Position slider** — use the postion slider to go through the satellites position at any point along orbit, with the satellite's live X/Y/Z coordinates
- **Error handling** — catches any network timeouts, connection failures and HTTP errors from Celestrak, fetching back to the last cached satellite
- **Manual refresh** —
Sidebar button that re-fetches the satellite catalog from Celestrak

## How it works

Satellite positions are calculated using the [SGP4 orbital propagation model](https://en.wikipedia.org/wiki/Simplified_perturbations_models) via the [Skyfield](https://rhodesmill.org/skyfield/) library. Orbital data comes from [Celestrak](https://celestrak.org/) in TLE (Two-Line Element) format, which describes a satellite's orbit as of the exact moment the data was last measured. SGP4 propagates that orbit forward or backward in time to estimate position, accounting for effects native to Earth (e.g. atmospheric drag)

## Setup

```bash
pip install streamlit numpy requests plotly skyfield
streamlit run app.py
```

## Tech stack

- **Streamlit** — web app framework
- **Skyfield** — SGP4 orbital propagation
- **Plotly** — 3D visualization
- **Celestrak API** — live TLE satellite data

## Notes

This project first started as an ISS-exclusive visualixation, but from there it grew to satellite search, dropdown menus, catalogs, and error handling. The error handling was built with AI assistance from Claude, but the core orbit visualization was written almost entirely independently with some consultation from Google webpages. 

## Possible next steps

- Collision proximity detection between two or more satellites
- Satellite fuel burn analysis when avoiding collisions
- Historical vs. predicted orbit comparison