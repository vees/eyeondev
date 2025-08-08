#!/usr/bin/env python3
"""
Combine: township border + development points + light basemap → JPG
"""

import json
import geopandas as gpd
import matplotlib
import datetime
"""
A crash was happening because on macOS the default GUI backend for Matplotlib 
tries to open an NSWindow—and you’re running this in a background thread 
(or without a real display), so AppKit refuses. For a headless/cron‐style 
render (just writing out a JPG), the simplest fix is to switch Matplotlib 
to a non‐GUI (“Agg”) backend.
"""
matplotlib.use('Agg')       # use the Anti-Grain Geometry backend — no GUI
import matplotlib.pyplot as plt
from shapely.geometry import Point
import contextily as ctx
from matplotlib.offsetbox import AnchoredText

plt.ioff()

class RenderFeature:
    def render(self, geocode_result=None):
        # ---------- Inputs ----------
        BOUNDARY_GEOJSON = "lower_salford_boundary.geojson"
        DEV_JSON         = "development_entries_geocoded.json"
        OUT_JPG          = "development_map_with_basemap.jpg"
        ZOOM             = 14  # 13–16 are good for township scale

        # ---------- Load data ----------
        # Boundary
        boundary_gdf = gpd.read_file(BOUNDARY_GEOJSON).to_crs(epsg=3857)

        dev_raw = geocode_result or {}
        if not dev_raw:
            with open(DEV_JSON) as f:
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
        ax.set_title("Lower Salford Township - Eye on Development", fontsize=16)
        ax.legend(title="Development Status", loc='lower right')
        ax.set_axis_off()

        today = datetime.datetime.now().strftime("%B %d, %Y")
        stamp = AnchoredText(f"Data from: June 26, 2025, Generated: {today}", loc='lower left', prop=dict(size=8), frameon=True)
        stamp.patch.set_alpha(0.7)
        ax.add_artist(stamp)

        # ---------- Save ----------
        fig.savefig(OUT_JPG, dpi=300, bbox_inches='tight')
        plt.close(fig)

        return({'image_url': "/image".format(file=OUT_JPG)})
    
if __name__ == "__main__":
    renderer = RenderFeature()
    result = renderer.render()
    print(result)
