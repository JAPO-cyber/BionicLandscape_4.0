import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
        /* 🌄 Sfondo visivo per tutta l'app */
        .stApp {
            background-image: url("https://raw.githubusercontent.com/JAPO-cyber/BionicLandscape_4.0/main/assets/bg.jpg"); /* sfondo remoto */
            background-size: cover;               /* copre tutta la finestra */
            background-attachment: fixed;         /* resta fisso durante lo scroll */
            background-repeat: no-repeat;         /* no ripetizioni */
            background-position: center;          /* centrato */
        }

        /* 🧱 Contenitore centrale con sfondo semi-trasparente per migliorare leggibilità */
        .block-container {
            background-color: rgba(255, 255, 255, 0.85);  /* sfondo bianco trasparente */
            border-radius: 15px;                          /* angoli arrotondati */
            padding: 2rem 1rem 4rem 1rem;                 /* spaziatura interna */
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);  /* ombra leggera */
        }

        /* 🔘 Pulsanti con stile coerente alla palette Bionic Landscape */
        .stButton button {
            width: 100%;                      /* larghezza piena */
            padding: 1rem;                    /* più area cliccabile */
            font-size: 1.1rem;                /* testo più leggibile */
            border-radius: 10px;              /* angoli morbidi */
            margin-top: 1rem;                 /* distanziamento dall’elemento sopra */
            background-color: #2B7A78;        /* verde acqua */
            color: white;                     /* testo chiaro */
            border: none;
        }

        /* 🔘 Hover con transizione fluida */
        .stButton button:hover {
            background-color: #20504f;        /* verde più scuro al passaggio */
            transition: background-color 0.3s ease;
        }

        /* 🧭 Sidebar: aggiungi padding e stile se vuoi usarla per stato utente o navigazione */
        .css-1d391kg {  /* classe dinamica della sidebar in Streamlit */
            padding-top: 2rem;
        }

        /* 📱 Mobile responsiveness */
        @media only screen and (max-width: 600px) {
            .stButton button {
                font-size: 1rem;              /* testo leggermente più piccolo */
                padding: 0.8rem;              /* pulsanti più compatti */
            }

            .block-container {
                padding: 1rem;                /* meno padding su mobile */
            }
        }

        /* 🏷️ Header personalizzabile (se vuoi usare un titolo centrale) */
        .header {
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1.5rem;
            color: #17252A;
        }
        </style>
    """, unsafe_allow_html=True)
