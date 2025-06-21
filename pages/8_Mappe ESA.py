# pages/4_Visualizza_Mappa.py

import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster, HeatMap, MeasureControl, Draw, MousePosition

# ─── Configurazione pagina Streamlit ──────────────────────────────────────
st.set_page_config(page_title="Mappa Bergamo GIS", layout="wide")
st.title("🌍 Visualizzazione GIS - Bergamo con Dati ESA")

# ─── Sidebar: selezioni layer e strumenti ─────────────────────────────────
st.sidebar.header("Configurazione Mappa")
# Basemap
basemaps = {
    'OpenStreetMap': 'OpenStreetMap',
    'Stamen Terrain': 'Stamen Terrain',
    'Esri Satellite': 'Esri WorldImagery'
}
basemap_choice = st.sidebar.selectbox("Scegli basemap:", list(basemaps.keys()), index=0)

# ESA WMTS layers disponibili
esa_layers = {
    'WorldCover 2021': 'WorldCover_2021_v200',
    'Sentinel-2 NDVI (demo)': 'NDVI_S2_L2A'  # endpoint ipotetico
}
esa_choice = st.sidebar.selectbox("Layer ESA:", list(esa_layers.keys()))
opacity = st.sidebar.slider("Opacità layer ESA", min_value=0.0, max_value=1.0, value=0.6)

# Filtri punti di interesse
points = [
    {"id": "P1", "lat": 45.6983, "lon": 9.6773, "label": "Centro Bergamo",  "category": "Turismo",    "popup": "Centro storico di Bergamo"},
    {"id": "P2", "lat": 45.7280, "lon": 9.6775, "label": "Città Alta",       "category": "Storico",   "popup": "Città Alta"},
    {"id": "P3", "lat": 45.6512, "lon": 9.6648, "label": "Stazione FS",     "category": "Trasporti", "popup": "Stazione ferroviaria"},
    {"id": "P4", "lat": 45.7047, "lon": 9.6454, "label": "Ospedale",        "category": "Sanitario", "popup": "Ospedale Papa Giovanni XXIII"},
]
categories = sorted({p["category"] for p in points})
selected_categories = st.sidebar.multiselect("Filtra categorie:", options=categories, default=categories)
show_heatmap = st.sidebar.checkbox("Mostra heatmap", value=False)
cluster_markers = st.sidebar.checkbox("Cluster markers", value=True)
use_measure = st.sidebar.checkbox("Abilita misurazione (MeasureControl)", value=True)
use_draw = st.sidebar.checkbox("Abilita disegno (Draw)", value=False)
show_coords = st.sidebar.checkbox("Mostra coordinate (MousePosition)", value=True)

# ─── Costruzione mappa Folium ─────────────────────────────────────────────
# Centro su Bergamo
m = folium.Map(
    location=[45.6983, 9.6773],
    zoom_start=13,
    tiles=basemaps[basemap_choice]
)

# Aggiungi plugin opzionali
if use_measure:
    m.add_child(MeasureControl())
if use_draw:
    m.add_child(Draw(export=True))
if show_coords:
    m.add_child(MousePosition())

# Aggiungo layer ESA WMTS
folium.raster_layers.WmsTileLayer(
    url="https://worldcover2021.esa.int/mapproxy/wmts",
    name=f"ESA {esa_choice}",
    layers=esa_layers[esa_choice],
    fmt="image/png",
    transparent=True,
    opacity=opacity,
    tile_size=256,
    attr="ESA Standard"
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

# ─── Debug: dati lato client ────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.write(f"Punti mostrati: {len(filtered)}")
st.sidebar.dataframe(filtered)

