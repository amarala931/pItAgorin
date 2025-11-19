import streamlit as st
from PIL import Image
import os
from src.backend.knowledge_base import KnowledgeBase
from src.ui.sidebar import render_sidebar
from src.ui.main_panel import render_main_panel

def load_assets():
    """
    Carga los recursos estáticos desde la carpeta local 'assets' dentro de UI.
    """
    # Obtenemos el directorio donde vive ESTE archivo (src/ui/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Buscamos en la carpeta assets vecina
    logo_path = os.path.join(current_dir, "assets", "logo.png")

    try:
        return Image.open(logo_path)
    except FileNotFoundError:
        # Retornamos None si no existe para que la UI use el fallback
        return None

def init_ui():
    """
    Orquestador principal de la interfaz.
    """
    # 1. Cargar Assets
    logo_img = load_assets()
    # Si hay logo usamos la imagen, si no, el emoji de serpiente
    page_icon = logo_img if logo_img else "🐍"

    # 2. Configuración de Página
    st.set_page_config(
        page_title="pItAgorin",
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 3. CSS Global
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] { display: none; }
        img { border-radius: 8px; }
        </style>
    """, unsafe_allow_html=True)

    # 4. Inicializar Backend
    @st.cache_resource
    def get_db_instance():
        return KnowledgeBase()
    
    db = get_db_instance()

    # 5. Renderizar Componentes
    config = render_sidebar(db, logo_img)
    render_main_panel(db, config, logo_img)