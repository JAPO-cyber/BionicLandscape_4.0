# pages/4_Visualizza_Mappa.py

import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster, HeatMap, MeasureControl, Draw, MousePosition

# ─── Configurazione pagina Streamlit ──────────────────────────────────────
st.set_page_config(page_title="Mappa Bergamo GIS", layout="wide")
st.title("🌍 Visualizzazione GIS - Sovrapposizione Layer")

# ─── Definizione Basemaps ───────────────────────────────────────────────────
basemaps = {
    'OpenStreetMap': 'OpenStreetMap',
    'Stamen Terrain': 'Stamen Terrain',
    'Stamen Toner': 'Stamen Toner',
    'Esri Satellite': 'Esri.WorldImagery',
    'CartoDB Positron': 'CartoDB.Positron'
}

# ─── Definizione Servizi (ESA, RL, BG) ──────────────────────────────────────
esa_services = {
    'ESA WorldCover 2021': {
        'url': 'https://worldcover2021.esa.int/mapproxy/wmts',
        'layers': 'WorldCover_2021_v200'
    },
    'ESA CCI Land Cover': {
        'url': 'https://services.esa.int/corine/wmts',
        'layers': 'CLC2018'
    },
    'EOX Sentinel-2 Cloudless': {
        'url': 'https://tiles.maps.eox.at/wmts',
        'layers': 's2cloudless-2019'
    }
}
region_services = {
    'Carta Fisica RL': {
        'url': 'https://www.cartografia.servizirl.it/arcgis2/services/wms/fisica_wms/MapServer/WMSServer?',
        'layers': None
    },
    'Zone Vulnerabili Nitrati': {
        'url': 'https://www.cartografia.servizirl.it/arcgis2/services/ambiente/Zone_vulnerabili_nitrati/MapServer/WMSServer?',
        'layers': None
    },
    'Grandi Strutture Vendita': {
        'url': 'https://www.cartografia.servizirl.it/arcgis2/services/commercio/GrandiStruttureVendita/MapServer/WMSServer?',
        'layers': None
    }
}
bg_services = {
    'Aree di Sosta': {
        'url': 'https://www.comune.bergamo.it/arcgis/services/AtlanteBG/AreeSosta/MapServer/WMSServer?',
        'layers': '0'
    },
    'Piste Ciclabili': {
        'url': 'https://www.comune.bergamo.it/arcgis/services/AtlanteBG/Ciclabili/MapServer/WMSServer?',
        'layers': '0'
    }
}
# Unione di tutti i servizi con nome unico
all_services = {**esa_services, **region_services, **bg_services}

# ─── Sidebar: selezioni e controlli ─────────────────────────────────────────
st.sidebar.header("Configurazione Mappa")
# Basemap single choice
basemap_choice = st.sidebar.selectbox("Basemap:", list(basemaps.keys()))
# Multilayer selection (sovrapposizione)
layers_choice = st.sidebar.multiselect(
    "Seleziona uno o più layer da sovrapporre:",
    options=list(all_services.keys()),
    default=list(all_services.keys())  # carica tutte le mappe di default
)

# Opacità comune per tutti i layer
opacity = st.sidebar.slider("Opacità layer WMS/WMTS", 0.0, 1.0, 0.6)
# Plugin interattivi
toggle_measure = st.sidebar.checkbox("Misurazione distanze/aree", value=True)
toggle_draw = st.sidebar.checkbox("Strumenti disegno", value=False)
toggle_coords = st.sidebar.checkbox("Mostra lat/lon", value=True)
# POI e filtri
poi_categories = ["Turismo","Storico","Trasporti","Sanitario"]
selected_cats = st.sidebar.multiselect("Filtra POI per categoria:", options=poi_categories, default=poi_categories)
toggle_heatmap = st.sidebar.checkbox("Heatmap POI", value=False)
toggle_cluster = st.sidebar.checkbox("Cluster POI", value=True)

# ─── Dati di esempio: POI ───────────────────────────────────────────────────
points = [
    {"id": "P1", "lat": 45.6983, "lon": 9.6773, "label": "Centro Bergamo", "category": "Turismo"},
    {"id": "P2", "lat": 45.7280, "lon": 9.6775, "label": "Città Alta",    "category": "Storico"},
    {"id": "P3", "lat": 45.6512, "lon": 9.6648, "label": "Staz. FS",      "category": "Trasporti"},
    {"id": "P4", "lat": 45.7047, "lon": 9.6454, "label": "Ospedale BG",  "category": "Sanitario"},
]
filtered = [p for p in points if p['category'] in selected_cats]
coords = [[p['lat'], p['lon']] for p in filtered]

# ─── Costruzione mappa Folium ─────────────────────────────────────────────
m = folium.Map(location=[45.6983, 9.6773], zoom_start=13, tiles=None)
# Aggiunta basemap
folium.TileLayer(tiles=basemaps[basemap_choice], name=basemap_choice, attr=basemap_choice).add_to(m)
# Plugin
if toggle_measure:
    m.add_child(MeasureControl())
if toggle_draw:
    m.add_child(Draw(export=True))
if toggle_coords:
    m.add_child(MousePosition())

# Aggiunta di tutti i layer selezionati
for key in layers_choice:
    svc = all_services[key]
    # Se è un WMTS (ha 'layers'), usiamo WmsTileLayer con parametro layers
    if svc.get('layers'):
        folium.raster_layers.WmsTileLayer(
            url=svc['url'],
            name=key,
            layers=svc['layers'],
            fmt="image/png",
            transparent=True,
            opacity=opacity,
            tile_size=256,
            attr="OGC"
        ).add_to(m)
    else:
        # Per WMS server che non richiedono 'layers' o lo inferiscono tutti
        folium.raster_layers.WmsTileLayer(
            url=svc['url'],
            name=key,
            fmt="image/png",
            transparent=True,
            opacity=opacity,
            tile_size=256,
            attr="OGC"
        ).add_to(m)

# POI: heatmap o cluster
if toggle_heatmap:
    HeatMap(coords, name="Heatmap POI").add_to(m)
elif toggle_cluster:
    cl = MarkerCluster(name="Cluster POI").add_to(m)
    for p in filtered:
        folium.Marker([p['lat'], p['lon']], tooltip=p['label']).add_to(cl)
else:
    for p in filtered:
        folium.Marker([p['lat'], p['lon']], tooltip=p['label']).add_to(m)

# Controllo layer e render
folium.LayerControl().add_to(m)
st_data = st_folium(m, width=900, height=600)

# Debug sidebar
st.sidebar.markdown("---")
st.sidebar.write(f"POI mostrati: {len(filtered)}")
st.sidebar.dataframe(filtered)
