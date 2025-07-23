import json
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# --- Step 1: Load Geocoded Development Entries ---
with open("development_entries_geocoded.json", "r") as f:
    data = json.load(f)

records = []
for category, entries in data.items():
    for entry in entries:
        lat = entry.get("latitude")
        lon = entry.get("longitude")
        if lat is not None and lon is not None:
            records.append({
                "category": category,
                "address": entry["address"],
                "description": entry["description"],
                "geometry": Point(lon, lat)
            })

gdf_points = gpd.GeoDataFrame(records, crs="EPSG:4326")

# --- Step 2: Load Township Boundary ---
boundary_gdf = gpd.read_file("lower_salford_boundary.geojson")

# --- Step 3: Plot Boundary + Points ---
fig, ax = plt.subplots(figsize=(10, 10))

# Plot township outline
boundary_gdf.boundary.plot(ax=ax, color='black', linewidth=1)

# Plot development markers, grouped by category
for category, group in gdf_points.groupby("category"):
    group.plot(ax=ax, marker='o', label=category, alpha=0.8)

# Final touches
ax.set_title("Lower Salford Development Map", fontsize=16)
ax.legend(title="Development Status", loc='upper right')
ax.set_axis_off()

# --- Step 4: Save Output ---
fig.savefig("development_map.jpg", dpi=300, bbox_inches='tight')
