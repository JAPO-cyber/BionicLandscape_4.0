import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
        /* 🌄 Sfondo visivo per tutta l'app */
        .stApp {
            background-image: url("https://raw.githubusercontent.com/JAPO-cyber/BionicLandscape_4.0/main/assets/bg.jpg");
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
        }

        /* 🧱 Contenitore centrale con sfondo bianco leggibile */
        .block-container {
            background-color: #ffffff;  /* bianco pieno */
            border-radius: 15px;        /* angoli arrotondati */
            padding: 2rem 1rem 4rem 1rem;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);  /* ombra visibile */
            backdrop-filter: blur(4px);  /* effetto blur dello sfondo dietro (opzionale) */
        }

        /* 🔘 Pulsanti con stile coerente alla palette Bionic Landscape */
        .stButton button {
            width: 100%;
            padding: 1rem;
            font-size: 1.1rem;
            border-radius: 10px;
            margin-top: 1rem;
            background-color: #2B7A78;   /* verde acqua */
            color: white;
            border: none;
        }

        /* 🔘 Hover con transizione fluida */
        .stButton button:hover {
            background-color: #20504f;
            transition: background-color 0.3s ease;
        }

        /* 🧭 Sidebar */
        .css-1d391kg {
            padding-top: 2rem;
        }

        /* 📱 Mobile responsiveness */
        @media only screen and (max-width: 600px) {
            .stButton button {
                font-size: 1rem;
                padding: 0.8rem;
            }
            .block-container {
                padding: 1rem;
            }
        }

        /* 🏷️ Header personalizzabile per login o titoli centrali */
        .header {
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1.5rem;
            color: #17252A;
        }
        </style>
    """, unsafe_allow_html=True)
