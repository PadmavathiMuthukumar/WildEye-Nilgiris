import geopandas as gpd
import matplotlib.pyplot as plt

# --- Load all shapefiles ---
nilgiris_poly = gpd.read_file("preprocessed/Nilgiris_polygon.shp")
forests = gpd.read_file("preprocessed/Nilgiris_forests_with_distance.shp")
roads = gpd.read_file("preprocessed/Nilgiris_roads.shp")
villages = gpd.read_file("preprocessed/Nilgiris_villages.shp")

# --- Fix missing CRS ---
if roads.crs is None:
    roads = roads.set_crs(epsg=4326)
if villages.crs is None:
    villages = villages.set_crs(epsg=4326)
if forests.crs is None:
    forests = forests.set_crs(epsg=4326)
if nilgiris_poly.crs is None:
    nilgiris_poly = nilgiris_poly.set_crs(epsg=4326)

# --- 1️⃣ Visualize Nilgiris Polygon ---
plt.figure(figsize=(8,8))
nilgiris_poly.boundary.plot(color='green', linewidth=2)
plt.title("Nilgiris District Boundary")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()

# --- 2️⃣ Visualize Protected Forests ---
plt.figure(figsize=(8,8))
forests.plot(column='dist_to_vi', cmap='YlGn', legend=True,
             legend_kwds={'label': "Distance to Village (m)"}, edgecolor='black')
plt.title("Protected Forests (Colored by Distance to Villages)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()

# --- 3️⃣ Visualize Roads ---
plt.figure(figsize=(8,8))
roads.plot(color='gray', linewidth=1)
plt.title("Road Network in Nilgiris")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()

# --- 4️⃣ Visualize Villages ---
plt.figure(figsize=(8,8))
villages.plot(color='red', markersize=30)
plt.title("Village Locations in Nilgiris")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()

# --- 5️⃣ Combined Visualization ---
fig, ax = plt.subplots(figsize=(10,10))
nilgiris_poly.boundary.plot(ax=ax, color='green', linewidth=2, label='Nilgiris Boundary')
forests.plot(ax=ax, column='dist_to_vi', cmap='YlGn', alpha=0.6, edgecolor='black', legend=True)
roads.plot(ax=ax, color='gray', linewidth=0.8, label='Roads')
villages.plot(ax=ax, color='red', markersize=25, label='Villages')

plt.title("Nilgiris — Protected Forests, Roads & Villages")
plt.xlabel("Longitude")
plt.ylabel("Latitude")

# Proxy legend handles
import matplotlib.lines as mlines
boundary_patch = mlines.Line2D([], [], color='green', label='Nilgiris Boundary')
road_line = mlines.Line2D([], [], color='gray', linewidth=1.5, label='Roads')
village_dot = mlines.Line2D([], [], color='red', marker='o', linestyle='None', markersize=8, label='Villages')

ax.legend(handles=[boundary_patch, road_line, village_dot], loc='upper right')

plt.show()

import geopandas as gpd
import matplotlib.pyplot as plt

# -----------------------------
# Load layers
# -----------------------------
forests = gpd.read_file("preprocessed/Nilgiris_protected_forests.shp")
roads = gpd.read_file("preprocessed/Nilgiris_roads.shp")
villages = gpd.read_file("preprocessed/Nilgiris_villages.shp")
grid = gpd.read_file("preprocessed/Nilgiris_grid.shp")  # Your existing grid file

# -----------------------------
# Fix CRS if missing
# -----------------------------
for gdf in [forests, roads, villages, grid]:
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)

# Optional: project to metric CRS for better visualization
forests_proj = forests.to_crs(epsg=3857)
roads_proj = roads.to_crs(epsg=3857)
villages_proj = villages.to_crs(epsg=3857)
grid_proj = grid.to_crs(epsg=3857)

# -----------------------------
# Plotting
# -----------------------------
fig, ax = plt.subplots(figsize=(12,12))

# Protected forests
forests_proj.plot(ax=ax, color='green', alpha=0.4, edgecolor='black', label='Protected Forests')

# Grid
grid_proj.boundary.plot(ax=ax, color='grey', linewidth=0.5, alpha=0.7, label='Grid Cells')

# Roads
roads_proj.plot(ax=ax, color='black', linewidth=0.7, label='Roads')

# Villages
villages_proj.plot(ax=ax, color='red', markersize=20, label='Villages')

# Title and labels
plt.title("Nilgiris: Protected Forests, Grid, Roads & Villages")
plt.xlabel("Longitude")
plt.ylabel("Latitude")

# Custom legend
import matplotlib.lines as mlines
forest_patch = mlines.Line2D([], [], color='green', marker='s', linestyle='None', markersize=10, label='Protected Forests')
grid_line = mlines.Line2D([], [], color='grey', linewidth=1, label='Grid Cells')
road_line = mlines.Line2D([], [], color='black', linewidth=1.5, label='Roads')
village_dot = mlines.Line2D([], [], color='red', marker='o', linestyle='None', markersize=8, label='Villages')

ax.legend(handles=[forest_patch, grid_line, road_line, village_dot], loc='upper right')

plt.show()
