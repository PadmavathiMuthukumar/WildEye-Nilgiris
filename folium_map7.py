import folium
import geopandas as gpd
import pandas as pd

# ----------------------------
# Load GeoJSON and Poaching Points
# ----------------------------
geojson_path = "results/Nilgiris_risk_grid_final.geojson"
gdf = gpd.read_file(geojson_path)

# Filter strictly for Nilgiri district only
if 'NAME' in gdf.columns:
    gdf = gdf[gdf['NAME'].str.contains("Nilgiri", case=False, na=False)]
elif 'DISTRICT' in gdf.columns:
    gdf = gdf[gdf['DISTRICT'].str.contains("Nilgiri", case=False, na=False)]

# If you have poaching points, load them
try:
    poach_points = gpd.read_file("results/poaching_points.geojson")
    # Filter poaching points to only those within Nilgiri bounds if needed
except:
    poach_points = gpd.GeoDataFrame()

# ----------------------------
# Define Risk Colors with Outline
# ----------------------------
def risk_color(risk):
    if risk == "High":
        return "red"
    elif risk == "Medium":
        return "yellow"
    else:
        return "green"

# ----------------------------
# Create Folium Map Centered on Nilgiri
# ----------------------------
# Get the bounds of filtered Nilgiri data for proper centering
if not gdf.empty:
    bounds = gdf.total_bounds
    center = [(bounds[1] + bounds[3])/2, (bounds[0] + bounds[2])/2]
else:
    center = [11.4, 76.7]  # Fallback center

m = folium.Map(location=center, zoom_start=10, tiles='OpenStreetMap')

# ----------------------------
# Add Forest Risk Zones with Outline
# ----------------------------
for _, row in gdf.iterrows():
    color = risk_color(row['risk'])
    
    sim_geo = folium.GeoJson(
        data=row['geometry'].__geo_interface__,
        style_function=lambda feature, color=color: {
            'fillColor': color,
            'color': color,  # This creates the outline
            'weight': 2,     # Thicker outline for better visibility
            'fillOpacity': 0.4,
            'opacity': 0.8   # Outline opacity
        }
    )
    
    popup_text = (
        f"<b>Grid ID:</b> {row['FID']}<br>"
        f"<b>Total Area:</b> {row['total_area']:.2f} m²<br>"
        f"<b>Dist. to Road:</b> {row['dist_road']:.2f} m<br>"
        f"<b>Dist. to Village:</b> {row['dist_village']:.2f} m<br>"
        f"<b>Risk:</b> {row['risk']}<br>"
        f"<b>Poaching Count:</b> {row['poaching_count']}"
    )
    sim_geo.add_child(folium.Popup(popup_text, max_width=300))
    sim_geo.add_to(m)

# ----------------------------
# Add Poaching Points (if available)
# ----------------------------
if not poach_points.empty:
    for _, row in poach_points.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=6,
            color="black",
            weight=1,
            fill=True,
            fill_color="orange",
            fill_opacity=0.9,
            popup=folium.Popup("Poaching Point", max_width=200)
        ).add_to(m)

# ----------------------------
# Add Legend
# ----------------------------
legend_html = '''
<div style="
    position: fixed; 
    bottom: 50px; left: 50px; width: 160px; height: 120px; 
    border:2px solid grey; z-index:9999; font-size:14px;
    background-color:white; padding:10px;">
<b>Nilgiri District - Risk Map</b><br>
<i style="background:red; width:15px; height:15px; float:left; margin-right:8px; border:1px solid black;"></i> High Risk<br>
<i style="background:yellow; width:15px; height:15px; float:left; margin-right:8px; border:1px solid black;"></i> Medium Risk<br>
<i style="background:lightgreen; width:15px; height:15px; float:left; margin-right:8px; border:1px solid black;"></i> Low Risk<br>
<i style="background:orange; width:15px; height:15px; float:left; margin-right:8px; border:1px solid black;"></i> Poaching Points
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# ----------------------------
# Save and Show Map
# ----------------------------
m.save("results/Nilgiris_Risk_Map.html")
print("✅ Nilgiri District Map saved successfully! Open: results/Nilgiris_Risk_Map.html")