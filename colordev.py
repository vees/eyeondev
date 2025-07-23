import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

# Load boundary and points (already in EPSG:4326)
boundary_gdf = gpd.read_file("lower_salford_boundary.geojson")

# Convert to Web Mercator (required by contextily)
boundary_web = boundary_gdf.to_crs(epsg=3857)

# Plot with contextily basemap
fig, ax = plt.subplots(figsize=(10, 10))

boundary_web.boundary.plot(ax=ax, edgecolor="black", linewidth=1)

# Add basemap tiles from Carto Light
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, attribution=False)

# Optional: Limit to bounds of boundary
ax.set_xlim(*boundary_web.total_bounds[[0, 2]])
ax.set_ylim(*boundary_web.total_bounds[[1, 3]])
ax.set_axis_off()

fig.savefig("development_map_with_basemap.jpg", dpi=300, bbox_inches='tight')

