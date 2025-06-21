# pages/4_Visualizza_Mappa.py

import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import WmtsTileLayer

# ─── Configurazione pagina ──────────────────────────────────────────────────
st.set_page_config(page_title="Piste Ciclabili su ESA", layout="wide")
st.title("🗺️ Piste Ciclabili di Bergamo su ESA WorldCover")

# ─── Costanti ──────────────────────────────────────────────────────────────
# Centro e zoom
CENTER = [45.6983, 9.6773]
ZOOM = 13

# ESA WorldCover basemap (WMTS)
ESA_WMTS_URL = "https://worldcover2021.esa.int/mapproxy/wmts"
ESA_WMTS_LAYER = "WorldCover_2021_v200"

# WMS Piste Ciclabili Comune di Bergamo
CICLABILI_WMS_URL = (
    "https://territorio.comune.bergamo.it/arcgis/services/"
    "AtlanteBG/Ciclabili/MapServer/WMSServer?"
)
CICLABILI_LAYER = "1"

# ─── Widget Sidebar ────────────────────────────────────────────────────────
st.sidebar.header("Opzioni Visualizzazione")
opacity = st.sidebar.slider("Opacità piste ciclabili", 0.1, 1.0, 0.8)

# ─── Creazione mappa Folium ───────────────────────────────────────────────
# Mappa senza tiles
m = folium.Map(location=CENTER, zoom_start=ZOOM, tiles=None)

# Aggiungi basemap ESA WMTS
WmtsTileLayer(
    url=ESA_WMTS_URL,
    name=\"ESA WorldCover\",
    tilematrixset=\"EPSG:4326\",
    fmt=\"image/png\",
    layers=ESA_WMTS_LAYER,
    attr=\"ESA WorldCover\",
    transparent=False,
    opacity=1.0,
    tile_size=256
).add_to(m)

# Aggiungi overlay piste ciclabili
folium.raster_layers.WmsTileLayer(
    url=CICLABILI_WMS_URL,
    name="Piste Ciclabili",
    layers=CICLABILI_LAYER,
    fmt="image/png",
    transparent=True,
    version="1.3.0",
    crs="EPSG:4326",
    opacity=opacity,
    attr="Comune di Bergamo"
).add_to(m)

# Controllo layer e render
folium.LayerControl(position='topright').add_to(m)
st_folium(m, width=900, height=600)

