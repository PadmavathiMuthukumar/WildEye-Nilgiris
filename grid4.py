import geopandas as gpd
from shapely.geometry import box
import numpy as np

# Load forests
forests = gpd.read_file("preprocessed/Nilgiris_protected_forests.shp")

# Define grid size (e.g., 1 km x 1 km)
grid_size = 1000  # in meters

# Project to metric CRS for accurate grid
forests_proj = forests.to_crs(epsg=3857)

# Get bounds
minx, miny, maxx, maxy = forests_proj.total_bounds

# Create grid cells
x_coords = np.arange(minx, maxx, grid_size)
y_coords = np.arange(miny, maxy, grid_size)
grid_cells = []

for x in x_coords:
    for y in y_coords:
        grid_cells.append(box(x, y, x + grid_size, y + grid_size))

grid = gpd.GeoDataFrame({'geometry': grid_cells}, crs=forests_proj.crs)

# Clip grid to forest area
grid_clipped = gpd.clip(grid, forests_proj)

grid_clipped.to_file("preprocessed/Nilgiris_grid.shp")
print(f"✅ Grid created with {len(grid_clipped)} cells over protected forests")
