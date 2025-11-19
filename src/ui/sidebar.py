import streamlit as st
from config.settings import MODEL_CATALOG

def render_sidebar(db_instance):
    """
    Renders the sidebar widgets and returns the user configuration.
    
    Args:
        db_instance: The instance of the KnowledgeBase class.
        
    Returns:
        dict: A dictionary containing 'rag_topics' and 'pipeline_steps'.
    """
    config = {
        "rag_topics": [],
        "pipeline_steps": []
    }
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # --- Section 1: RAG Context ---
        st.subheader("1. Knowledge Base Context")
        available_topics = db_instance.get_topics()
        
        # Multiselect to filter DB queries by specific topics
        config["rag_topics"] = st.multiselect(
            "Consult knowledge from:", 
            options=available_topics,
            placeholder="Select topics..."
        )
        
        st.divider()
        
        # --- Section 2: Model Pipeline ---
        st.subheader("2. Model Pipeline")
        
        # Dropdown to select a model from settings.py
        selected_model_name = st.selectbox(
            "Select Model", 
            list(MODEL_CATALOG.keys())
        )
        
        # Button to add the selected model to the execution queue
        if st.button("➕ Add Step"):
            if 'pipeline' not in st.session_state:
                st.session_state['pipeline'] = []
            
            # Retrieve model config from catalog and append to state
            model_info = MODEL_CATALOG[selected_model_name]
            st.session_state['pipeline'].append(model_info)
            
        # --- Pipeline Visualization ---
        st.write("---")
        st.write("**Execution Sequence:**")
        
        if 'pipeline' in st.session_state and st.session_state['pipeline']:
            for i, step in enumerate(st.session_state['pipeline']):
                # Display the model ID simply
                st.code(f"{i+1}. {step['model_id']}")
            
            # Button to clear the sequence
            if st.button("🗑️ Clear Pipeline"):
                st.session_state['pipeline'] = []
                st.rerun()
                
            config["pipeline_steps"] = st.session_state['pipeline']
        else:
            st.info("No models added yet.")
            
    return config