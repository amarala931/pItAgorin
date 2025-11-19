import streamlit as st
from config.settings import MODEL_CATALOG

def render_sidebar(db_instance, logo_img=None):
    config = {
        "rag_topics": [],
        "pipeline_steps": []
    }
    
    with st.sidebar:
        # --- LOGO ÁREA ---
        if logo_img:
            st.image(logo_img, use_column_width=True)
        else:
            st.title("pItAgorin")
            
        st.markdown("---")
        st.header("⚙️ Configuration")
        
        # --- 1. RAG Section ---
        st.subheader("1. Context (RAG)")
        temas_disponibles = db_instance.get_topics()
        
        config["rag_topics"] = st.multiselect(
            "Consult knowledge from:", 
            options=temas_disponibles,
            placeholder="Select topics..."
        )
        
        st.divider()
        
        # --- 2. Model Section ---
        st.subheader("2. Model Pipeline")
        
        selected_model_name = st.selectbox("Select Model", list(MODEL_CATALOG.keys()))
        
        if st.button("➕ Add Step"):
            if 'pipeline' not in st.session_state: st.session_state['pipeline'] = []
            model_info = MODEL_CATALOG[selected_model_name]
            st.session_state['pipeline'].append(model_info)
            
        st.write("**Sequence:**")
        if 'pipeline' in st.session_state and st.session_state['pipeline']:
            for i, step in enumerate(st.session_state['pipeline']):
                st.code(f"{i+1}. {step['model_id']}")
            
            if st.button("🗑️ Clear Pipeline"):
                st.session_state['pipeline'] = []
                st.rerun()  
            config["pipeline_steps"] = st.session_state['pipeline']
        else:
            st.caption("No models added yet.")
            
    return config