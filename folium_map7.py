import folium
import geopandas as gpd

# ----------------------------
# Load Data
# ----------------------------
grid_gdf = gpd.read_file("results/Nilgiris_risk_grid_final.geojson")
points_gdf = gpd.read_file("results/poaching_points.geojson")

# Convert CRS to EPSG:4326 for Folium
if grid_gdf.crs and grid_gdf.crs.to_string() != "EPSG:4326":
    grid_gdf = grid_gdf.to_crs(epsg=4326)
if points_gdf.crs and points_gdf.crs.to_string() != "EPSG:4326":
    points_gdf = points_gdf.to_crs(epsg=4326)

# ----------------------------
# Filter Risk Zones (High & Low only)
# ----------------------------
grid_gdf = grid_gdf[grid_gdf["risk"].isin(["High", "Low"])]

# ----------------------------
# Create Map Centered on Nilgiris
# ----------------------------
bounds = grid_gdf.total_bounds
center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]

m = folium.Map(location=center, zoom_start=12, tiles="CartoDB positron")

# ----------------------------
# Add Risk Zones Layer
# ----------------------------
def risk_color(risk):
    return "red" if risk == "High" else "green"

folium.GeoJson(
    grid_gdf,
    name="Risk Zones",
    style_function=lambda feature: {
        "fillColor": risk_color(feature["properties"]["risk"]),
        "color": risk_color(feature["properties"]["risk"]),
        "weight": 1.2,
        "fillOpacity": 0.45,
        "opacity": 0.8,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["FID", "risk", "poaching_count"],
        aliases=["Grid ID:", "Risk Level:", "Poaching Count:"],
        localize=True
    ),
).add_to(m)

# ----------------------------
# Add Poaching Points Layer
# ----------------------------
for _, row in points_gdf.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=3,
        color="black",
        fill=True,
        fill_color="black",
        fill_opacity=0.9,
        tooltip="Poaching Point"
    ).add_to(m)

# ----------------------------
# Add Legend
# ----------------------------
legend_html = """
<div style="
    position: fixed;
    bottom: 50px; left: 50px; width: 210px;
    border: 2px solid #444; z-index: 9999; font-size: 14px;
    background-color: white; padding: 10px; border-radius: 10px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
<b>🦁 WildEye – Nilgiri Risk Map</b><br><br>
<i style='background:red; width:15px; height:15px; float:left; margin-right:8px;'></i> High Risk<br>
<i style='background:lightgreen; width:15px; height:15px; float:left; margin-right:8px;'></i> Low Risk<br>
<i style='background:black; width:15px; height:15px; float:left; margin-right:8px;'></i> Poaching Point
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# ----------------------------
# Save Single Map
# ----------------------------
m.save("results/Nilgiri_Risk_and_Points.html")
print("✅ Combined Nilgiri Map saved: results/Nilgiri_Risk_and_Points.html")
