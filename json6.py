import geopandas as gpd

# -----------------------------
# Load your grid
# -----------------------------
grid_gdf = gpd.read_file("results/Nilgiris_risk_grid.geojson")

# -----------------------------
# Load forest polygons with attributes
# -----------------------------
forests_gdf = gpd.read_file("preprocessed/Nilgiris_forests_with_distance.shp")

# -----------------------------
# Choose columns to merge
# -----------------------------
# Use GIS_AREA as Total forest area
# dist_to_ro and dist_to_vi are distances
forest_attrs = forests_gdf[['GIS_AREA', 'dist_to_ro', 'dist_to_vi', 'geometry']]

# -----------------------------
# Spatial join: add forest attributes to grid
# -----------------------------
grid_with_attrs = gpd.sjoin(
    grid_gdf, 
    forest_attrs, 
    how='left', 
    predicate='intersects'
)

# -----------------------------
# Rename columns for JS
# -----------------------------
grid_with_attrs = grid_with_attrs.rename(columns={
    'GIS_AREA': 'total_area',
    'dist_to_ro': 'dist_road',
    'dist_to_vi': 'dist_village'
})

# -----------------------------
# Save final GeoJSON for front-end
# -----------------------------
grid_with_attrs.to_file("results/Nilgiris_risk_grid_final.geojson", driver="GeoJSON")
print("✅ Grid with forest attributes saved for front-end!")
