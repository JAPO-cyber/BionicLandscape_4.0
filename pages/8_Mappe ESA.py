# pages/4_Visualizza_Mappa.py

import streamlit as st
from streamlit_folium import st_folium
import folium

# ─── Configurazione pagina ──────────────────────────────────────────────────
st.set_page_config(page_title="Piste Ciclabili su ESA", layout="wide")
st.title("🗺️ Piste Ciclabili di Bergamo su ESA WorldCover")

# ─── Costanti ──────────────────────────────────────────────────────────────
CENTER = [45.6983, 9.6773]  # Centro Bergamo
ZOOM = 13

# ─── Basemap ESA: scelta multipla ───────────────────────────────────────────
# Opzioni basemap ESA
basemap_options = {
    'Esri Satellite': {
        'type': 'provider',
        'tiles': 'Esri.WorldImagery',
        'attr': 'Esri'
    },
    'Sentinel-2 Cloudless': {
        'type': 'xyz',
        'url': 'https://tiles.maps.eox.at/v3/{z}/{x}/{y}.png',
        'attr': 'EOX Sentinel-2 Cloudless'
    },
    'WorldCover 2021': {
        'type': 'wmts',
        'url': 'https://worldcover2021.esa.int/mapproxy/wmts',
        'layers': 'WorldCover_2021_v200',
        'attr': 'ESA WorldCover 2021'
    },
    'CCI Land Cover': {
        'type': 'wms',
        'url': 'https://services.esa.int/corine/wmts',
        'layers': 'CLC2018',
        'fmt': 'image/png',
        'attr': 'ESA CCI Land Cover'
    }
}
    'Sentinel-2 Cloudless': {
        'type': 'xyz',
        'url': 'https://tiles.maps.eox.at/v3/{z}/{x}/{y}.png',
        'attr': 'EOX Sentinel-2 Cloudless'
    },
    'WorldCover 2021': {
        'type': 'wmts',
        'url': 'https://worldcover2021.esa.int/mapproxy/wmts',
        'layers': 'WorldCover_2021_v200',
        'attr': 'ESA WorldCover 2021'
    },
    'CCI Land Cover': {
        'type': 'wms',
        'url': 'https://services.esa.int/corine/wmts',
        'layers': 'CLC2018',
        'fmt': 'image/png',
        'attr': 'ESA CCI Land Cover'
    }
}
# Scegli basemap ESA
esa_choice = st.sidebar.selectbox("Basemap ESA:", list(basemap_options.keys()), index=0)

# Ciclabili WMS ArcGIS
CICLABILI_WMS_URL = (
    "https://territorio.comune.bergamo.it/arcgis/services/"
    "AtlanteBG/Ciclabili/MapServer/WMSServer?"
)
CICLABILI_LAYER = "1"


# ─── Sidebar ────────────────────────────────────────────────────────────────
st.sidebar.header("Opzioni Visualizzazione")
show_ciclabili = st.sidebar.checkbox("Mostra Piste Ciclabili", value=True)
opacity = st.sidebar.slider("Opacità Piste Ciclabili", min_value=0.1, max_value=1.0, value=0.8)

# ─── Creazione mappa Folium ───────────────────────────────────────────────
# Inizializza mappa senza basemap
m = folium.Map(location=CENTER, zoom_start=ZOOM, tiles=None)

# 1. Aggiungi basemap ESA in base alla scelta
bm = basemap_options[esa_choice]
if bm['type'] == 'xyz':
    folium.TileLayer(
        tiles=bm['url'],
        name=esa_choice,
        attr=bm['attr'],
        opacity=1.0,
        max_zoom=20
    ).add_to(m)
elif bm['type'] == 'wmts':
    folium.raster_layers.WmsTileLayer(
        url=bm['url'],
        name=esa_choice,
        layers=bm['layers'],
        fmt='image/png',
        transparent=False,
        opacity=1.0,
        tile_size=256,
        attr=bm['attr'],
        version='1.0.0'
    ).add_to(m)
else:
    folium.raster_layers.WmsTileLayer(
        url=bm['url'],
        name=esa_choice,
        layers=bm['layers'],
        fmt=bm.get('fmt','image/png'),
        transparent=False,
        opacity=1.0,
        version='1.3.0',
        crs='EPSG:4326',
        attr=bm['attr']
    ).add_to(m)

# 2. Overlay WMS Piste Ciclabili
if show_ciclabili:
    folium.raster_layers.WmsTileLayer(
        url=CICLABILI_WMS_URL,
        name="Piste Ciclabili",
        layers=CICLABILI_LAYER,
        fmt="image/png",
        transparent=True,
        version="1.1.1",
        crs="EPSG:4326",
        opacity=opacity,
        attr="Comune di Bergamo"
    ).add_to(m)

# 3. Fit al bounding box di Bergamo
# SW: (45.655085, 9.618587), NE: (45.731830, 9.714212)
m.fit_bounds([[45.655085, 9.618587], [45.731830, 9.714212]])

# 4. Controllo layer e render
folium.LayerControl(position='topright').add_to(m)
st_folium(m, width=900, height=600)

