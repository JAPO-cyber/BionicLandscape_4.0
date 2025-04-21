import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
        /* 🌄 Sfondo generale */
        .stApp {
            background-image: url("https://raw.githubusercontent.com/JAPO-cyber/BionicLandscape_4.0/main/assets/bg.jpg");
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
            color: #f5f5f5 !important;  /* testo chiaro globale */
        }

        /* 🧱 Sfondo per tutte le card/box/area centrale */
        .block-container {
            background-color: rgba(0, 0, 0, 0.85);  /* sfondo nero semi-opaco */
            border-radius: 15px;
            padding: 2rem 1rem 4rem 1rem;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.5);
        }

        /* ✍️ Input testo, select, textarea, slider */
        input, textarea, select {
            background-color: #111 !important;
            color: #f5f5f5 !important;
            border: 1px solid #444 !important;
        }

        /* 📑 Placeholder */
        ::placeholder {
            color: #aaa !important;
        }

        /* 🏷️ Etichette (label) */
        label, .css-1cpxqw2 {
            color: #f5f5f5 !important;
            font-weight: 600;
        }

        /* 🎛️ Radio e Checkbox */
        .stRadio, .stCheckbox, .stSelectbox {
            background-color: transparent !important;
            color: #f5f5f5 !important;
        }

        /* 🎚️ Slider: colore chiaro */
        .stSlider > div[data-baseweb="slider"] {
            background-color: #444;
        }

        /* 🔘 Pulsanti */
        .stButton button {
            width: 100%;
            padding: 1rem;
            font-size: 1.1rem;
            border-radius: 10px;
            margin-top: 1rem;
            background-color: #2B7A78 !important;
            color: white !important;
            font-weight: bold;
            border: none;
        }

        .stButton button:hover {
            background-color: #20504f !important;
            transition: background-color 0.3s ease;
        }

        /* 📱 Mobile */
        @media only screen and (max-width: 600px) {
            .stButton button {
                font-size: 1rem;
                padding: 0.8rem;
            }
        }

        /* 🏷️ Header centrale */
        .header {
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1.5rem;
            color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)


