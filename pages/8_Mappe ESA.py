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

# ─── Definizione Servizi (ESA, Regione Lombardia, Comune Bergamo) ────────────
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
        'layers': '0'
    },
    'Zone Vulnerabili Nitrati': {
        'url': 'https://www.cartografia.servizirl.it/arcgis2/services/ambiente/Zone_vulnerabili_nitrati/MapServer/WMSServer?',
        'layers': '0'
    },
    'Grandi Strutture Vendita': {
        'url': 'https://www.cartografia.servizirl.it/arcgis2/services/commercio/GrandiStruttureVendita/MapServer/WMSServer?',
        'layers': '0'
    }
}
bg_services = {
    'Aree di Sosta': {
        'url': 'https://territorio.comune.bergamo.it:443/arcgis/services/AtlanteBG/AreeSosta/MapServer/WMSServer?',
        'layers': '0'
    },
    'Piste Ciclabili': {
        'url': 'https://territorio.comune.bergamo.it:443/arcgis/services/AtlanteBG/Ciclabili/MapServer/WMSServer?',
        'layers': '1'
    }
}
# Unione di tutti i servizi
all_services = {**esa_services, **region_services, **bg_services}

# ─── Sidebar: selezioni e controlli ─────────────────────────────────────────
st.sidebar.header("Configurazione Mappa")
# Basemap single choice
basemap_choice = st.sidebar.selectbox("Basemap:", list(basemaps.keys()))
# Multilayer selection (sovrapposizione)
layers_choice = st.sidebar.multiselect(
    "Seleziona uno o più layer da sovrapporre:",
    options=list(all_services.keys()),
    default=list(all_services.keys())
)
# Opacità comune per tutti i layer
opacity = st.sidebar.slider("Opacità layer WMS/WMTS", 0.0, 1.0, 0.6)
# Plugin interattivi
toggle_measure = st.sidebar.checkbox("Misurazione distanze/aree", value=True)
toggle_draw = st.sidebar.checkbox("Strumenti disegno", value=False)
toggle_coords = st.sidebar.checkbox("Mostra lat/lon", value=True)
# POI e filtri
poi_categories = ["Turismo", "Storico", "Trasporti", "Sanitario"]
selected_cats = st.sidebar.multiselect(
    "Filtra POI per categoria:", options=poi_categories, default=poi_categories
)
toggle_heatmap = st.sidebar.checkbox("Heatmap POI", value=False)
toggle_cluster = st.sidebar.checkbox("Cluster POI", value=True)

# ─── Dati di esempio: POI ───────────────────────────────────────────────────
points = [
    {"id": "P1", "lat": 45.6983, "lon": 9.6773, "label": "Centro Bergamo", "category": "Turismo"},
    {"id": "P2", "lat": 45.7280, "lon": 9.6775, "label": "Città Alta",    "category": "Storico"},
    {"id": "P3", "lat": 45.6512, "lon": 9.6648, "label": "Staz. FS",      "category": "Trasporti"},
    {"id": "P4", "lat": 45.7047, "lon": 9.6454, "label": "Ospedale BG",  "category": "Sanitario"}
]
filtered = [p for p in points if p['category'] in selected_cats]
coords = [[p['lat'], p['lon']] for p in filtered]

# ─── Selezione mappe non ESA rapida ─────────────────────────────────────────
st.subheader("Mappe Regionali e Comunali — Selezione rapida")
non_esa_keys = list(region_services.keys()) + list(bg_services.keys())
selected_non_esa = st.multiselect(
    "Scegli mappe non ESA da sovrapporre:",
    options=non_esa_keys,
    default=non_esa_keys
)

# ─── Costruzione mappa Folium ─────────────────────────────────────────────
# Mappa principale
m = folium.Map(location=[45.6983, 9.6773], zoom_start=13, tiles=None)
# Aggiunta basemap
folium.TileLayer(
    tiles=basemaps[basemap_choice], name=basemap_choice, attr=basemap_choice
).add_to(m)
# Plugin
if toggle_measure:
    m.add_child(MeasureControl())
if toggle_draw:
    m.add_child(Draw(export=True))
if toggle_coords:
    m.add_child(MousePosition())
# Aggiunta tutti i layer selezionati
for key in layers_choice:
    svc = all_services[key]
    folium.raster_layers.WmsTileLayer(
        url=svc['url'],
        name=key,
        layers=svc['layers'],
        fmt="image/png",
        transparent=True,
        opacity=opacity,
        tile_size=256,
        attr="OGC WMTS/WMS"
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
# Layer control e render principale
folium.LayerControl().add_to(m)
st_data = st_folium(m, width=900, height=600)

# ─── Mappa secondaria: solo layer Comune di Bergamo ─────────────────────────
st.subheader("🗺️ Mappa Comune di Bergamo (solo layer comunali)")
m2 = folium.Map(location=[45.6983, 9.6773], zoom_start=13, tiles=None)
folium.TileLayer(
    tiles=basemaps[basemap_choice], name=basemap_choice, attr=basemap_choice
).add_to(m2)
# Debug info: URL e layers
st.write("**Debug BG Services**")
for key in bg_services:
    svc = bg_services[key]
    st.write(f"- {key}: url={svc['url']} layers={svc['layers']}")
    try:
        folium.raster_layers.WmsTileLayer(
            url=svc['url'],
            name=key,
            layers=svc['layers'],
            fmt="image/png",
            transparent=True,
            opacity=opacity,
            tile_size=256,
            version='1.3.0',
            attr="Comune di Bergamo"
        ).add_to(m2)
    except Exception as e:
        st.error(f"Errore caricamento layer {key}: {e}")
# Controllo layer e render secondario
folium.LayerControl().add_to(m2)
st_folium(m2, width=900, height=600)

# Debug sidebar
st.sidebar.markdown("---")
st.sidebar.write(f"POI mostrati: {len(filtered)}")
st.sidebar.dataframe(filtered)
