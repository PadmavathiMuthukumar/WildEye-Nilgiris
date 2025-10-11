import geopandas as gpd
import osmnx as ox
import matplotlib.pyplot as plt
import os

# -----------------------------
# Setup folders
# -----------------------------
os.makedirs("preprocessed", exist_ok=True)

# -----------------------------
# Step 1: Get Nilgiris polygon from OSM
# -----------------------------
nilgiris_poly = ox.geocode_to_gdf("Nilgiris, Tamil Nadu, India")
nilgiris_poly.to_file("preprocessed/Nilgiris_polygon.shp")
print("✅ Nilgiris polygon saved and loaded.")

# -----------------------------
# Step 2: Load WDPA polygons (India)
# -----------------------------
wdpa = gpd.read_file(
    r"C:/Users/padma/OneDrive/ドキュメント/Desktop/Wildeye/data/WDPA_WDOECM_Oct2025_Public_IND_shp/WDPA_WDOECM_Oct2025_Public_IND_shp_2/WDPA_WDOECM_Oct2025_Public_IND_shp-polygons.shp"
)

# Filter WDPA polygons for Nilgiris-area forests
keywords = ["Mudumalai", "Mukurthi", "Sathyamangalam", "Silent Valley", "Western Ghats"]
nilgiri_forests = wdpa[wdpa["NAME"].str.contains("|".join(keywords), case=False, na=False)]

# Clip forests to Nilgiris
nilgiris_poly = nilgiris_poly.to_crs(wdpa.crs)
nilgiri_forests_clipped = gpd.clip(nilgiri_forests, nilgiris_poly)
nilgiri_forests_clipped.to_file("preprocessed/Nilgiris_protected_forests.shp")
print(f"✅ Protected forests clipped and saved: {len(nilgiri_forests_clipped)} areas.")

# -----------------------------
# Step 3: Load Southern Region Roads and Villages
# -----------------------------
roads_gdf = gpd.read_file(
    r"C:/Users/padma/OneDrive/ドキュメント/Desktop/Wildeye/data/osm/gis_osm_roads_free_1.shp"
)
villages_gdf = gpd.read_file(
    r"C:/Users/padma/OneDrive/ドキュメント/Desktop/Wildeye/data/osm/gis_osm_places_a_free_1.shp"
)
print("✅ Southern region roads and villages loaded.")

# -----------------------------
# Step 4: Clip Roads and Villages to Nilgiris
# -----------------------------
roads_nilgiris = gpd.clip(roads_gdf, nilgiris_poly)
villages_nilgiris = gpd.clip(villages_gdf, nilgiris_poly)

# Save the clipped data
roads_nilgiris.to_file("preprocessed/Nilgiris_roads.shp")
villages_nilgiris.to_file("preprocessed/Nilgiris_villages.shp")

print(f"✅ Roads clipped & saved: {len(roads_nilgiris)} | Villages clipped & saved: {len(villages_nilgiris)}")

# -----------------------------
# Step 5: Visualization
# -----------------------------
fig, ax = plt.subplots(figsize=(12, 12))

# Nilgiris boundary
nilgiris_poly.boundary.plot(ax=ax, edgecolor='green', linewidth=2, label='Nilgiris Boundary')

# Protected forests
nilgiri_forests_clipped.plot(ax=ax, color='darkgreen', edgecolor='black', alpha=0.6, label='Protected Forests')

# Roads
roads_nilgiris.plot(ax=ax, color='grey', linewidth=0.7, label='Roads')

# Villages
villages_nilgiris.plot(ax=ax, color='red', markersize=20, label='Villages')

plt.title("Protected Forests, Roads, and Villages in Nilgiris")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend()
plt.show()

# -----------------------------
# Step 6: Distance calculation
# -----------------------------
# -----------------------------
# Step 6: Distance calculation (fixed)
# -----------------------------
# -----------------------------
# Step 6: Distance calculation (fixed version)
# -----------------------------

# Step 6A — ensure all inputs have CRS before reprojection
if nilgiri_forests_clipped.crs is None:
    nilgiri_forests_clipped.set_crs(epsg=4326, inplace=True)
if roads_nilgiris.crs is None:
    roads_nilgiris.set_crs(epsg=4326, inplace=True)
if villages_nilgiris.crs is None:
    villages_nilgiris.set_crs(epsg=4326, inplace=True)

# Step 6B — reproject all to meters (for distance)
proj_crs = "EPSG:3857"
forests_proj = nilgiri_forests_clipped.to_crs(proj_crs)
roads_proj = roads_nilgiris.to_crs(proj_crs)
villages_proj = villages_nilgiris.to_crs(proj_crs)

# Step 6C — clean invalid geometries
forests_proj = forests_proj[~forests_proj.geometry.is_empty & forests_proj.geometry.is_valid]

# Step 6D — check if empty
if len(forests_proj) == 0:
    print("⚠️ No forest polygons found after clipping. Check CRS or keywords.")
else:
    # Step 6E — distance to nearest road
    forests_proj["dist_to_road_m"] = forests_proj.geometry.apply(
        lambda geom: roads_proj.distance(geom).min()
    )

    # Step 6F — distance to nearest village
    forests_proj["dist_to_village_m"] = forests_proj.geometry.apply(
        lambda geom: villages_proj.distance(geom).min()
    )

    # Step 6G — save results
    output_path = os.path.join("preprocessed", "Nilgiris_forests_with_distance.shp")
    forests_proj.to_file(output_path, driver="ESRI Shapefile")
    print(f"✅ Distance calculation complete and saved: {output_path}")

    # Step 6H — preview few results
    print(forests_proj[["NAME", "dist_to_road_m", "dist_to_village_m"]].head())
