import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt
import os

# -----------------------------
# Step 0: Setup folder
# -----------------------------
os.makedirs("preprocessed", exist_ok=True)

# -----------------------------
# Step 1: Get Nilgiris polygon from OSM
# -----------------------------
nilgiris_poly = ox.geocode_to_gdf("Nilgiris, Tamil Nadu, India")
nilgiris_poly.to_file("preprocessed/Nilgiris_polygon.shp")  # Save for later use

# -----------------------------
# Step 2: Load WDPA polygons (India)
# -----------------------------
wdpa = gpd.read_file(
    r"C:/Users/padma/OneDrive/ドキュメント/Desktop/Wildeye/data/WDPA_WDOECM_Oct2025_Public_IND_shp/WDPA_WDOECM_Oct2025_Public_IND_shp_2/WDPA_WDOECM_Oct2025_Public_IND_shp-polygons.shp"
)

# Explore available names
print("Available names:", wdpa["NAME"].unique())

# -----------------------------
# Step 3: Filter WDPA polygons for Nilgiris-area forests
# -----------------------------
keywords = ["Mudumalai", "Mukurthi", "Sathyamangalam", "Silent Valley", "Western Ghats"]
nilgiri_forests = wdpa[wdpa["NAME"].str.contains("|".join(keywords), case=False, na=False)]
print("Filtered areas:")
print(nilgiri_forests[["NAME", "DESIG_ENG", "STATUS"]])

# -----------------------------
# Step 4: Clip forests to Nilgiris polygon (✅ ensures no extra areas)
# -----------------------------
nilgiris_poly = nilgiris_poly.to_crs(wdpa.crs)  # Ensure CRS match
nilgiri_forests_clipped = gpd.clip(nilgiri_forests, nilgiris_poly)

# -----------------------------
# Step 5: Visualize clipped forests
# -----------------------------
fig, ax = plt.subplots(figsize=(12, 12))

# Nilgiris boundary
nilgiris_poly.boundary.plot(ax=ax, edgecolor='green', linewidth=2, label='Nilgiris Boundary')

# Protected forests inside Nilgiris only
nilgiri_forests_clipped.plot(ax=ax, color="darkgreen", edgecolor="black", alpha=0.6, label="Protected Forests")

plt.title("Protected Forests in and around Nilgiris District")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend()
plt.show()
