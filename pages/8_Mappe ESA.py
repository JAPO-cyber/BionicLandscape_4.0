# pages/4_Visualizza_Mappa.py

import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster, HeatMap, MeasureControl, Draw, MousePosition

# ─── Configurazione pagina Streamlit ──────────────────────────────────────
st.set_page_config(page_title="Mappa Bergamo GIS", layout="wide")
st.title("🌍 Visualizzazione GIS - Bergamo con Dati ESA e Basemaps Multipli")

# ─── Definizione Basemaps e Servizi ESA ────────────────────────────────────
basemaps = {
    'OpenStreetMap': 'OpenStreetMap',
    'Stamen Terrain': 'Stamen Terrain',
    'Stamen Toner': 'Stamen Toner',
    'Esri Satellite': 'Esri WorldImagery',
    'CartoDB Positron': 'CartoDB positron'
}

esa_services = {
    'WorldCover 2021': {
        'url': 'https://worldcover2021.esa.int/mapproxy/wmts',
        'layer': 'WorldCover_2021_v200'
    },
    'Sentinel-2 NDVI (demo)': {
        'url': 'https://tiles.example.com/wmts',  # esempio endpoint
        'layer': 'NDVI_S2_L2A'
    },
    'Copernicus CORINE Land Cover': {
        'url': 'https://services.esa.int/corine/wmts',  # esempio endpoint
        'layer': 'CLC2018'
    }
}

# ─── Sidebar: selezioni e controlli ────────────────────────────────────────
st.sidebar.header("Configurazione Mappa")
# Scegli Basemap
basemap_choice = st.sidebar.selectbox("Basemap:", list(basemaps.keys()), index=0)
# Scegli Servizio ESA
esa_choice = st.sidebar.selectbox("Servizio ESA (WMTS/WMS):", list(esa_services.keys()))
opacity = st.sidebar.slider("Opacità layer ESA", min_value=0.0, max_value=1.0, value=0.6)
# Filtri POI
toggle_heatmap = st.sidebar.checkbox("Heatmap POI", value=False)
toggle_cluster = st.sidebar.checkbox("Cluster POI", value=True)
toggle_measure = st.sidebar.checkbox("Misurazione distanze/aree", value=True)
toggle_draw = st.sidebar.checkbox("Strumenti disegno", value=False)
toggle_coords = st.sidebar.checkbox("Mostra lat/lon al passaggio", value=True)

# ─── Dati di esempio: POI a Bergamo ────────────────────────────────────────
points = [
    {"id": "P1", "lat": 45.6983, "lon": 9.6773, "label": "Centro Bergamo",  "category": "Turismo",    "popup": "Centro storico di Bergamo"},
    {"id": "P2", "lat": 45.7280, "lon": 9.6775, "label": "Città Alta",       "category": "Storico",   "popup": "Città Alta"},
    {"id": "P3", "lat": 45.6512, "lon": 9.6648, "label": "Stazione FS",     "category": "Trasporti", "popup": "Stazione ferroviaria"},
    {"id": "P4", "lat": 45.7047, "lon": 9.6454, "label": "Ospedale",        "category": "Sanitario", "popup": "Ospedale Papa Giovanni XXIII"},
]
categories = sorted({p['category'] for p in points})
selected_cats = st.sidebar.multiselect("Filtra categorie:", options=categories, default=categories)

# ─── Costruzione mappa Folium ─────────────────────────────────────────────
# Centro su Bergamo
m = folium.Map(
    location=[45.6983, 9.6773],
    zoom_start=13,
    tiles=basemaps[basemap_choice]
)
# Plugin
if toggle_measure:
    m.add_child(MeasureControl())
if toggle_draw:
    m.add_child(Draw(export=True))
if toggle_coords:
    m.add_child(MousePosition())

# Aggiungi layer ESA WMTS/WMS selezionato
svc = esa_services[esa_choice]
folium.raster_layers.WmsTileLayer(
    url=svc['url'],
    name=f"ESA: {esa_choice}",
    layers=svc['layer'],
    fmt="image/png",
    transparent=True,
    opacity=opacity,
    tile_size=256,
    attr="ESA / OGC WMTS/WMS"
).add_to(m)

# Filtro punti
filtered = [p for p in points if p['category'] in selected_cats]
coords = [[p['lat'], p['lon']] for p in filtered]

# Aggiungo HeatMap o Cluster
if toggle_heatmap:
    HeatMap(coords, name="Heatmap POI").add_to(m)
else:
    if toggle_cluster:
        cl = MarkerCluster(name="Cluster POI").add_to(m)
        for p in filtered:
            folium.Marker(location=[p['lat'], p['lon']], tooltip=p['label'], popup=p['popup']).add_to(cl)
    else:
        for p in filtered:
            folium.Marker(location=[p['lat'], p['lon']], tooltip=p['label'], popup=p['popup']).add_to(m)

# Controllo layer
folium.LayerControl().add_to(m)

# ─── Render su Streamlit ───────────────────────────────────────────────────
st_data = st_folium(m, width=900, height=600)

# ─── Debug ─────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.write(f"POI mostrati: {len(filtered)}")
st.sidebar.dataframe(filtered)

