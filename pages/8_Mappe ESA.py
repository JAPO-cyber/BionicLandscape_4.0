# pages/4_Visualizza_Mappa.py

import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster, HeatMap, MeasureControl, Draw, MousePosition

# ─── Configurazione pagina ──────────────────────────────────────────────────
st.set_page_config(page_title="Mappa Bergamo GIS", layout="wide")
st.title("🌍 Visualizzazione GIS - Sovrapposizione Layer")

# ─── Definizione Basemaps ───────────────────────────────────────────────────
basemaps = {
    'OpenStreetMap': 'OpenStreetMap',
    'Stamen Terrain': 'Stamen Terrain',
    'Stamen Toner': 'Stamen Toner',
    # ESRI satellite basemap from Leaflet providers (Esri.WorldImagery)
    'Esri Satellite': 'Esri.WorldImagery',
    'CartoDB Positron': 'CartoDB.Positron'
}

# ─── Definizione Servizi ─────────────────────────────────────────────────────
esa_services = {
    'ESA WorldCover 2021':    {'url': 'https://worldcover2021.esa.int/mapproxy/wmts', 'layers': 'WorldCover_2021_v200'},
    'ESA CCI Land Cover':     {'url': 'https://services.esa.int/corine/wmts', 'layers': 'CLC2018'},
    'EOX Sentinel-2 Cloudless': {'url': 'https://tiles.maps.eox.at/wmts', 'layers': 's2cloudless-2019'}
}
region_services = {
    'Carta Fisica RL':          {'url': 'https://www.cartografia.servizirl.it/arcgis2/services/wms/fisica_wms/MapServer/WMSServer?', 'layers': '0'},
    'Zone Vulnerabili Nitrati': {'url': 'https://www.cartografia.servizirl.it/arcgis2/services/ambiente/Zone_vulnerabili_nitrati/MapServer/WMSServer?', 'layers': '0'},
    'Grandi Strutture Vendita': {'url': 'https://www.cartografia.servizirl.it/arcgis2/services/commercio/GrandiStruttureVendita/MapServer/WMSServer?', 'layers': '0'}
}
bg_services = {
    'Aree di Sosta':   {'url': 'https://territorio.comune.bergamo.it/arcgis/services/AtlanteBG/AreeSosta/MapServer/WMSServer?', 'layers': '0'},
    'Piste Ciclabili': {'url': 'https://territorio.comune.bergamo.it/arcgis/services/AtlanteBG/Ciclabili/MapServer/WMSServer?', 'layers': '1'}
}
# Unione di tutti i servizi
all_services = {**esa_services, **region_services, **bg_services}

# ─── Sidebar di configurazione ──────────────────────────────────────────────
st.sidebar.header("Configurazione Mappa")
basemap_choice = st.sidebar.selectbox("Basemap:", list(basemaps.keys()))
layers_choice = st.sidebar.multiselect(
    "Seleziona layer da sovrapporre:",
    options=list(all_services.keys()),
    default=list(all_services.keys())
)
opacity = st.sidebar.slider("Opacità layer WMS/WMTS", 0.0, 1.0, 0.6)
toggle_measure = st.sidebar.checkbox("Misurazione distanze/aree", value=True)
toggle_draw    = st.sidebar.checkbox("Strumenti disegno", value=False)
toggle_coords  = st.sidebar.checkbox("Mostra lat/lon", value=True)
poi_categories = ["Turismo", "Storico", "Trasporti", "Sanitario"]
selected_cats  = st.sidebar.multiselect("Filtra POI:", options=poi_categories, default=poi_categories)
toggle_heatmap = st.sidebar.checkbox("Heatmap POI", value=False)
toggle_cluster = st.sidebar.checkbox("Cluster POI", value=True)

# ─── Dati di esempio: POI ───────────────────────────────────────────────────
points = [
    {"lat": 45.6983, "lon": 9.6773, "label": "Centro Bergamo", "cat": "Turismo"},
    {"lat": 45.7280, "lon": 9.6775, "label": "Città Alta", "cat": "Storico"},
    {"lat": 45.6512, "lon": 9.6648, "label": "Staz. FS", "cat": "Trasporti"},
    {"lat": 45.7047, "lon": 9.6454, "label": "Ospedale BG", "cat": "Sanitario"}
]
filtered = [p for p in points if p['cat'] in selected_cats]
coords = [[p['lat'], p['lon']] for p in filtered]

# ─── Mappa principale ───────────────────────────────────────────────────────
m = folium.Map(location=[45.6983, 9.6773], zoom_start=13, tiles=None)
# Basemap
folium.TileLayer(
    tiles=basemaps[basemap_choice], name=basemap_choice, attr=basemap_choice
).add_to(m)
# Plugin
if toggle_measure: m.add_child(MeasureControl())
if toggle_draw:   m.add_child(Draw(export=True))
if toggle_coords: m.add_child(MousePosition())
# Aggiunta layer WMS/WMTS
for key in layers_choice:
    svc = all_services[key]
    folium.raster_layers.WmsTileLayer(
        url=svc['url'], name=key, layers=svc['layers'],
        fmt="image/png", transparent=True, opacity=opacity,
        version="1.3.0", tile_size=256, attr="OGC"
    ).add_to(m)
# POI
if toggle_heatmap:
    HeatMap(coords, name="Heatmap").add_to(m)
elif toggle_cluster:
    cl = MarkerCluster(name="Cluster").add_to(m)
    for p in filtered:
        folium.Marker([p['lat'], p['lon']], tooltip=p['label']).add_to(cl)
else:
    for p in filtered:
        folium.Marker([p['lat'], p['lon']], tooltip=p['label']).add_to(m)
# Legend and render
folium.LayerControl().add_to(m)
st_data = st_folium(m, width=900, height=600)

# ─── Mappa secondaria: solo Piste Ciclabili su basemap ESA ─────────────────
st.subheader("🗺️ Mappa Comunale: Piste Ciclabili su ESA WorldCover")

# Costruzione mappa secondaria
m2 = folium.Map(location=[45.6983, 9.6773], zoom_start=13, tiles=None)

# Aggiunta basemap ESA WorldCover 2021
esa_base = esa_services['ESA WorldCover 2021']
folium.raster_layers.WmsTileLayer(
    url=esa_base['url'],
    name='Base ESA WorldCover',
    layers=esa_base['layers'],
    fmt='image/png',
    transparent=False,
    opacity=1.0,
    tile_size=256,
    attr='ESA WorldCover'
).add_to(m2)

# Overlay WMS per Piste Ciclabili
svc = bg_services['Piste Ciclabili']
folium.raster_layers.WmsTileLayer(
    url=svc['url'],
    name='Piste Ciclabili',
    layers=svc['layers'],
    fmt='image/png',
    transparent=True,
    opacity=opacity,
    version='1.3.0',
    crs='EPSG:4326',
    attr='Comune di Bergamo'
).add_to(m2)

# Controllo layer secondario e render
folium.LayerControl().add_to(m2)
st_folium(m2, width=900, height=600)

# Debug sidebar
st.sidebar.markdown("---")
st.sidebar.write(f"POI mostrati: {len(filtered)}")
st.sidebar.dataframe(filtered)

