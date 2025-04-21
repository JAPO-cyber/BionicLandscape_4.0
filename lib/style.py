import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
        /* 🌄 Sfondo dell'app */
        .stApp {
            background-image: url("https://raw.githubusercontent.com/JAPO-cyber/BionicLandscape_4.0/main/assets/bg.jpg");
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
            color: #111111; /* testo principale molto scuro */
        }

        /* ✅ Input testuale visibile */
        input, textarea {
            background-color: #ffffff !important;  /* bianco pieno */
            color: #111111 !important;             /* testo scuro */
            font-weight: 500;
        }

        /* ✅ Etichette e placeholder */
        label, .css-1cpxqw2 {  /* classi dinamiche Streamlit per etichette */
            color: #111111 !important;
            font-weight: 600;
        }

        /* ✅ Pulsanti ben visibili */
        .stButton button {
            width: 100%;
            padding: 1rem;
            font-size: 1.1rem;
            border-radius: 10px;
            margin-top: 1rem;
            background-color: #2B7A78 !important;   /* verde acqua */
            color: white !important;
            font-weight: bold;
            border: none;
        }

        .stButton button:hover {
            background-color: #20504f !important;   /* hover più scuro */
            transition: background-color 0.3s ease;
        }

        /* ✅ Titolo centrale opzionale */
        .header {
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1.5rem;
            color: #17252A;
        }

        /* 📱 Responsive */
        @media only screen and (max-width: 600px) {
            .stButton button {
                font-size: 1rem;
                padding: 0.8rem;
            }
        }
        </style>
    """, unsafe_allow_html=True)

