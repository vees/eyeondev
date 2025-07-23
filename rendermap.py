import geopandas as gpd
import matplotlib.pyplot as plt

# Load the boundary GeoJSON file
gdf = gpd.read_file("lower_salford_boundary.geojson")

# Plot and export
fig, ax = plt.subplots(figsize=(8, 8))
gdf.boundary.plot(ax=ax, linewidth=1, color='black')

# Optional: customize background, labels, etc.
ax.set_title("Eye on Development", fontsize=16)
ax.set_axis_off()

# Save to JPG
fig.savefig("lower_salford_map.jpg", format="jpg", dpi=300, bbox_inches='tight')
