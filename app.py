import streamlit as st
from src.backend.knowledge_base import KnowledgeBase
from src.ui.sidebar import render_sidebar
from ui.main_panel import render_main_panel

# 1. Global Page Configuration
# Sets the browser tab title, favicon, and layout mode.
st.set_page_config(
    page_title="pItAgorin",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """
    Main application entry point.
    Orchestrates the flow between the UI and the Backend.
    """
    
    # 2. Initialize the Knowledge Base (Singleton Pattern)
    # We use @st.cache_resource to load the DB and Embedding Model only once.
    # This prevents reloading the heavy models every time the user clicks a button.
    @st.cache_resource
    def get_db_instance():
        return KnowledgeBase()
    
    # Get the active instance of the database
    db = get_db_instance()

    # 3. Render the Sidebar
    # This function draws the sidebar and returns the user's configuration (selected models, RAG topics).
    config = render_sidebar(db)

    # 4. Render the Main Panel
    # We pass the DB instance (to save data) and the config (to know what to execute).
    render_main_panel(db, config)

if __name__ == "__main__":
    main()