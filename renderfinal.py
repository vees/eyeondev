#!/usr/bin/env python3
"""
Combine: township border + development points + light basemap → JPG
"""

import json
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import contextily as ctx

# ---------- Inputs ----------
BOUNDARY_GEOJSON = "lower_salford_boundary.geojson"
DEV_JSON         = "development_entries_geocoded.json"
OUT_JPG          = "development_map_with_basemap.jpg"
ZOOM             = 14  # 13–16 are good for township scale

# ---------- Load data ----------
# Boundary
boundary_gdf = gpd.read_file(BOUNDARY_GEOJSON).to_crs(epsg=3857)

# Development entries (already geocoded)
with open(DEV_JSON, "r") as f:
    dev_raw = json.load(f)

records = []
for category, entries in dev_raw.items():
    for e in entries:
        lat, lon = e.get("latitude"), e.get("longitude")
        if lat is None or lon is None:
            continue
        records.append({
            "category": category,
            "address": e["address"],
            "description": e["description"],
            "geometry": Point(lon, lat)
        })

gdf_points = gpd.GeoDataFrame(records, crs="EPSG:4326").to_crs(epsg=3857)

# ---------- Plot ----------
fig, ax = plt.subplots(figsize=(10, 10))

# Set extent BEFORE adding tiles so contextily knows what to fetch
xmin, ymin, xmax, ymax = boundary_gdf.total_bounds
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)

# Basemap (underlay)
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, attribution=False, zoom=ZOOM)

# Boundary (outline)
boundary_gdf.boundary.plot(ax=ax, edgecolor='black', linewidth=1)

# Points by category
for cat, grp in gdf_points.groupby("category"):
    grp.plot(ax=ax, marker='o', alpha=0.85, label=cat)

# Cosmetics
ax.set_title("Lower Salford Development Map", fontsize=16)
ax.legend(title="Development Status", loc='lower right')
ax.set_axis_off()

# ---------- Save ----------
fig.savefig(OUT_JPG, dpi=300, bbox_inches='tight')
