# pages/4_Visualizza_Mappa.py

import streamlit as st
from streamlit_folium import st_folium
import folium


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

# Aggiungi basemap ESA basata su XYZ (EOX Sentinel-2 Cloudless come proxy ESA)
folium.TileLayer(
    tiles=(
        "https://tiles.maps.eox.at/wmts?"  
        "SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=s2cloudless-2019&STYLE=&"
        "TILEMATRIXSET=GoogleMapsCompatible&FORMAT=image%2Fjpeg&"
        "TileMatrix={z}&TileRow={y}&TileCol={x}"
    ),
    name="ESA Sentinel-2 Cloudless",
    attr="EOX Sentinel-2 Cloudless",
    opacity=1.0,
    max_zoom=20
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

