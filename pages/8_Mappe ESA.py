# pages/4_Visualizza_Mappa.py

import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster, HeatMap, MeasureControl, Draw, MousePosition

# ─── Configurazione pagina Streamlit ──────────────────────────────────────
st.set_page_config(page_title="Mappa Bergamo GIS", layout="wide")
st.title("🌍 Visualizzazione GIS - Bergamo con Dati ESA e Basemaps")

# ─── Definizione Basemaps e Servizi ESA ────────────────────────────────────
# Tiles provider (OGC, Esri, Carto, Stamen)
basemaps = {
    'OpenStreetMap': 'OpenStreetMap',
    'Stamen Terrain': 'Stamen Terrain',
    'Stamen Toner': 'Stamen Toner',
    'Esri Satellite': 'Esri.WorldImagery',
    'CartoDB Positron': 'CartoDB.Positron'
}

esa_services = {
    'WorldCover 2021': {
        'url': 'https://worldcover2021.esa.int/mapproxy/wmts',
        'layer': 'WorldCover_2021_v200'
    },
    'Sentinel-2 NDVI (demo)': {
        'url': 'https://tiles.example.com/wmts',  # endpoint di esempio
        'layer': 'NDVI_S2_L2A'
    },
    'Copernicus CORINE Land Cover': {
        'url': 'https://services.esa.int/corine/wmts',
        'layer': 'CLC2018'
    }
}

# ─── Sidebar: selezioni e controlli ────────────────────────────────────────
st.sidebar.header("Configurazione Mappa")
basemap_choice = st.sidebar.selectbox("Basemap:", list(basemaps.keys()), index=0)
esa_choice = st.sidebar.selectbox("Servizio ESA:", list(esa_services.keys()), index=0)
opacity = st.sidebar.slider("Opacità ESA layer", 0.0, 1.0, 0.6)
toggle_heatmap = st.sidebar.checkbox("Heatmap POI", value=False)
toggle_cluster = st.sidebar.checkbox("Cluster POI", value=True)
toggle_measure = st.sidebar.checkbox("Misurazione distanze/aree", value=True)
toggle_draw = st.sidebar.checkbox("Strumenti disegno", value=False)
toggle_coords = st.sidebar.checkbox("Mostra lat/lon", value=True)
selected_cats = st.sidebar.multiselect("Filtra categorie:", options=["Turismo","Storico","Trasporti","Sanitario"], default=["Turismo","Storico","Trasporti","Sanitario"])

# ─── Dati di esempio: POI a Bergamo ────────────────────────────────────────
points = [
    {"id": "P1", "lat": 45.6983, "lon": 9.6773, "label": "Centro Bergamo",  "category": "Turismo",    "popup": "Centro storico di Bergamo"},
    {"id": "P2", "lat": 45.7280, "lon": 9.6775, "label": "Città Alta",       "category": "Storico",   "popup": "Città Alta"},
    {"id": "P3", "lat": 45.6512, "lon": 9.6648, "label": "Stazione FS",     "category": "Trasporti", "popup": "Stazione ferroviaria"},
    {"id": "P4", "lat": 45.7047, "lon": 9.6454, "label": "Ospedale",        "category": "Sanitario", "popup": "Ospedale Papa Giovanni XXIII"},
]
filtered = [p for p in points if p['category'] in selected_cats]
coords = [[p['lat'], p['lon']] for p in filtered]

# ─── Costruzione mappa Folium ─────────────────────────────────────────────
# Inizializzo mappa senza basemap di default
m = folium.Map(location=[45.6983, 9.6773], zoom_start=13, tiles=None)

# Aggiungo basemap selezionato
folium.TileLayer(
    tiles=basemaps[basemap_choice],
    name=basemap_choice,
    attr=basemap_choice
).add_to(m)

# Plugin interattivi
if toggle_measure:
    m.add_child(MeasureControl())
if toggle_draw:
    m.add_child(Draw(export=True))
if toggle_coords:
    m.add_child(MousePosition())

# Aggiungi layer ESA selezionato
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

# Aggiunta punti: heatmap o cluster
if toggle_heatmap:
    HeatMap(coords, name="Heatmap POI").add_to(m)
elif toggle_cluster:
    cl = MarkerCluster(name="Cluster POI").add_to(m)
    for p in filtered:
        folium.Marker([p['lat'], p['lon']], tooltip=p['label'], popup=p['popup']).add_to(cl)
else:
    for p in filtered:
        folium.Marker([p['lat'], p['lon']], tooltip=p['label'], popup=p['popup']).add_to(m)

# Controllo layer e render
folium.LayerControl().add_to(m)
st_data = st_folium(m, width=900, height=600)

# ─── Debug ─────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.write(f"POI mostrati: {len(filtered)}")
st.sidebar.dataframe(filtered)
