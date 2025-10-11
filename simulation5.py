'''import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os
from shapely.geometry import Point, Polygon

# -----------------------------
# Folders
# -----------------------------
os.makedirs("results", exist_ok=True)

# -----------------------------
# Load Nilgiris protected forest polygons
# -----------------------------
forests_shp = "preprocessed/Nilgiris_forests_with_distance.shp"
forests_gdf = gpd.read_file(forests_shp)

# -----------------------------
# Simulate poaching points
# -----------------------------
# Parameters
points_per_forest = 50  # number of poaching points per forest polygon (adjustable)
simulated_points = []

for idx, row in forests_gdf.iterrows():
    polygon = row.geometry
    minx, miny, maxx, maxy = polygon.bounds
    
    # Generate random points inside polygon
    count = 0
    while count < points_per_forest:
        x = np.random.uniform(minx, maxx)
        y = np.random.uniform(miny, maxy)
        pt = Point(x, y)
        if polygon.contains(pt):
            simulated_points.append(pt)
            count += 1

# Create GeoDataFrame
poaching_gdf = gpd.GeoDataFrame(geometry=simulated_points, crs=forests_gdf.crs)

# Save simulated poaching points
poaching_shp_path = "results/simulated_poaching.shp"
poaching_gdf.to_file(poaching_shp_path)
print(f"✅ Simulated poaching points saved: {len(poaching_gdf)} points.")

# -----------------------------
# Visualization
# -----------------------------
fig, ax = plt.subplots(figsize=(12,12))

# Forest polygons (light green)
forests_gdf.plot(ax=ax, color='lightgreen', edgecolor='black', alpha=0.5, label='Protected Forests')

# Simulated poaching points (black x)
poaching_gdf.plot(ax=ax, color='black', marker='x', markersize=20, label='Simulated Poaching')

plt.title("Nilgiris: Protected Forests & Simulated Poaching Zones")
plt.xlabel("Longitude")
plt.ylabel("Latitude")

# Custom legend
import matplotlib.lines as mlines
forest_patch = mlines.Line2D([], [], color='lightgreen', marker='s', markersize=10, linestyle='None', label='Protected Forests')
poaching_dot = mlines.Line2D([], [], color='black', marker='x', markersize=8, linestyle='None', label='Poaching Points')
ax.legend(handles=[forest_patch, poaching_dot], loc='upper right')

plt.tight_layout()
plt.show()
'''
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from shapely.geometry import Point

# -----------------------------
# Folders
# -----------------------------
os.makedirs("results", exist_ok=True)

# -----------------------------
# Load Nilgiris protected forest polygons
# -----------------------------
forests_shp = "preprocessed/Nilgiris_forests_with_distance.shp"
forests_gdf = gpd.read_file(forests_shp)

# -----------------------------
# Load forest stats CSV
# -----------------------------
stats_csv = "data/file.csv"
stats_df = pd.read_csv(stats_csv)
stats_df = stats_df.set_index("District")  # optional, to map later if needed

# -----------------------------
# Simulate poaching points per forest polygon
# -----------------------------
simulated_points = []

for idx, row in forests_gdf.iterrows():
    polygon = row.geometry
    # Use Total forest area to scale number of poaching points
    forest_area = row.get("Total", 50)  # fallback
    points_per_forest = max(5, int(forest_area * 0.5))  # adjust factor for reasonable points
    
    minx, miny, maxx, maxy = polygon.bounds
    count = 0
    while count < points_per_forest:
        x = np.random.uniform(minx, maxx)
        y = np.random.uniform(miny, maxy)
        pt = Point(x, y)
        if polygon.contains(pt):
            simulated_points.append(pt)
            count += 1

# Create GeoDataFrame
poaching_gdf = gpd.GeoDataFrame(geometry=simulated_points, crs=forests_gdf.crs)
poaching_shp_path = "results/simulated_poaching.shp"
poaching_gdf.to_file(poaching_shp_path)
print(f"✅ Simulated poaching points saved: {len(poaching_gdf)} points.")

# -----------------------------
# Create grid (if not already)
# -----------------------------
grid_shp = "preprocessed/Nilgiris_grid.shp"
grid_gdf = gpd.read_file(grid_shp)

# -----------------------------
# Count poaching points in each grid
# -----------------------------
poaching_sindex = poaching_gdf.sindex

def count_in_cell(cell_geom):
    candidates = poaching_gdf.iloc[list(poaching_sindex.intersection(cell_geom.bounds))]
    return candidates.within(cell_geom).sum()

grid_gdf['poaching_count'] = grid_gdf.geometry.apply(count_in_cell)

# -----------------------------
# Define dynamic risk levels (percentile-based)
# -----------------------------
low_thresh = np.percentile(grid_gdf['poaching_count'], 33)
high_thresh = np.percentile(grid_gdf['poaching_count'], 66)

def risk_level(count):
    if count <= low_thresh:
        return "Low"
    elif count <= high_thresh:
        return "Medium"
    else:
        return "High"

grid_gdf['risk'] = grid_gdf['poaching_count'].apply(risk_level)

# -----------------------------
# Risk colors
# -----------------------------
risk_colors = {"Low": "lightgreen", "Medium": "yellow", "High": "red"}

# -----------------------------
# Visualization
# -----------------------------
fig, ax = plt.subplots(figsize=(12,12))
forests_gdf.plot(ax=ax, color='lightgrey', edgecolor='black', alpha=0.3, label='Protected Forests')
grid_gdf.plot(ax=ax, color=grid_gdf['risk'].map(risk_colors), edgecolor='black', alpha=0.5)

# Optional: show simulated points (for debugging)
poaching_gdf.plot(ax=ax, color='black', marker='x', markersize=10, label='Poaching Points')

plt.title("Nilgiris: Poaching Risk Zones")
plt.xlabel("Longitude")
plt.ylabel("Latitude")

import matplotlib.patches as mpatches
forest_patch = mpatches.Patch(color='lightgrey', label='Protected Forests')
low_patch = mpatches.Patch(color='lightgreen', label='Low Risk')
medium_patch = mpatches.Patch(color='yellow', label='Medium Risk')
high_patch = mpatches.Patch(color='red', label='High Risk')
ax.legend(handles=[forest_patch, low_patch, medium_patch, high_patch], loc='upper right')

plt.tight_layout()
plt.show()
# Save final risk grid as GeoJSON for front-end use
grid_geojson_path = "results/Nilgiris_risk_grid.geojson"
grid_gdf.to_file(grid_geojson_path, driver="GeoJSON")
print(f"✅ Risk grid saved as GeoJSON: {grid_geojson_path}")
