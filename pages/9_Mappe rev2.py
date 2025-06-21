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

# ESA Basemap (EOX Sentinel-2 Cloudless proxy WMTS)
ESA_TILE_URL = (
    "https://tiles.maps.eox.at/wmts?"
    "SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=s2cloudless-2019&STYLE=&"
    "TILEMATRIXSET=GoogleMapsCompatible&FORMAT=image%2Fjpeg&"
    "TileMatrix={z}&TileRow={y}&TileCol={x}"
)

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
m = folium.Map(location=CENTER, zoom_start=ZOOM, tiles=None)

# 1. Aggiungi basemap ESA
folium.TileLayer(
    tiles=ESA_TILE_URL,
    name="ESA Satellite (Sentinel-2 Cloudless)",
    attr="EOX Sentinel-2 Cloudless",
    opacity=1.0,
    max_zoom=20
).add_to(m)

# 2. Overlay WMS Piste Ciclabili
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

# 3. Fit to Bergamo bounding box
m.fit_bounds([[45.655085, 9.618587], [45.731830, 9.714212]])

# 4. Controllo layer e render
folium.LayerControl(position='topright').add_to(m)
st_folium(m, width=900, height=600)

