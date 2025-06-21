# pages/4_Visualizza_Mappa.py

import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster, HeatMap

# ─── Configurazione pagina Streamlit ──────────────────────────────────────
st.set_page_config(page_title="Mappa Bergamo GIS", layout="wide")
st.title("🌍 Visualizzazione GIS - Bergamo")

# ─── Parametri ESA WMTS (esempio WorldCover 2021) ───────────────────────────
wmts_url = "https://worldcover2021.esa.int/mapproxy/wmts"
wmts_layer = "WorldCover_2021_v200"
wmts_format = "image/png"
wmts_opacity = 0.6

# ─── Dati di esempio: punti d'interesse a Bergamo ───────────────────────────
points = [
    {"id": "P1", "lat": 45.6983, "lon": 9.6773, "label": "Centro Bergamo",  "category": "Turismo", "popup": "Centro storico di Bergamo"},
    {"id": "P2", "lat": 45.7280, "lon": 9.6775, "label": "Città Alta",       "category": "Storico", "popup": "Città Alta"},
    {"id": "P3", "lat": 45.6512, "lon": 9.6648, "label": "Stazione FS",     "category": "Trasporti", "popup": "Stazione ferroviaria"},
    {"id": "P4", "lat": 45.7047, "lon": 9.6454, "label": "Ospedale",        "category": "Sanitario", "popup": "Ospedale Papa Giovanni XXIII"},
]

# ─── Sidebar: filtri e controlli ─────────────────────────────────────────────
categories = sorted({p["category"] for p in points})
selected_categories = st.sidebar.multiselect(
    label="Filtra categorie:",
    options=categories,
    default=categories
)
show_heatmap = st.sidebar.checkbox("Mostra heatmap", value=False)
cluster_markers = st.sidebar.checkbox("Cluster markers", value=True)

# ─── Costruzione mappa Folium ─────────────────────────────────────────────
# Centro su Bergamo
m = folium.Map(location=[45.6983, 9.6773], zoom_start=13, tiles="OpenStreetMap")

# Aggiungo layer ESA WMTS
folium.raster_layers.WmsTileLayer(
    url=wmts_url,
    name="ESA WorldCover 2021",
    layers=wmts_layer,
    fmt=wmts_format,
    transparent=True,
    opacity=wmts_opacity,
    tile_size=256,
    attr="ESA WorldCover"
).add_to(m)

# Preparo dati filtrati
filtered = [p for p in points if p["category"] in selected_categories]
coords = [[p["lat"], p["lon"]] for p in filtered]

# Aggiungo HeatMap o MarkerCluster
if show_heatmap:
    HeatMap(coords, name="Heatmap punti").add_to(m)
else:
    if cluster_markers:
        cluster = MarkerCluster(name="Cluster punti").add_to(m)
        for p in filtered:
            folium.Marker(
                location=[p["lat"], p["lon"]],
                popup=p["popup"],
                tooltip=p["label"],
            ).add_to(cluster)
    else:
        for p in filtered:
            folium.Marker(
                location=[p["lat"], p["lon"]],
                popup=p["popup"],
                tooltip=p["label"],
            ).add_to(m)

# Controlli layer
folium.LayerControl().add_to(m)

# ─── Render su Streamlit ───────────────────────────────────────────────────
st_data = st_folium(m, width=800, height=600)

# Debug: visualizzo dati lato client
st.sidebar.markdown("---")
st.sidebar.write(f"Punti mostrati: {len(filtered)}")
st.sidebar.dataframe(filtered)
