import streamlit as st
from src.backend.model_engine import execute_pipeline

def render_main_panel(db_instance, config):
    """
    Renders the main workspace area with file upload capabilities.
    """
    # Header with the project name
    st.title("🐍 pItAgorin")
    st.markdown("### AI Orchestrator & Local Knowledge Base")

    # --- Knowledge Ingestion Section (Updated with File Upload) ---
    with st.expander("📚 Feed Knowledge Base (Upload Data)", expanded=False):
        
        # We use tabs to organize input methods cleanly
        tab_manual, tab_upload = st.tabs(["✍️ Manual Text", "📁 Upload File"])
        
        # Variables to hold the content to be saved
        content_to_save = ""
        source_name = "manual"
        
        with tab_manual:
            manual_text = st.text_area("Paste text content here:", height=150)
            
        with tab_upload:
            # Accepts .txt and .md files (safe text formats)
            uploaded_file = st.file_uploader("Upload a document", type=["txt", "md"])

        # Common controls for both tabs
        col_meta, col_btn = st.columns([3, 1])
        
        with col_meta:
            topic_tag = st.text_input("Topic / Tag (e.g., Finance, History)", "General")
            
        with col_btn:
            st.write("") # Spacer for alignment
            st.write("") 
            save_btn = st.button("💾 Save to DB", use_container_width=True)

        # Logic to process the input when Save is clicked
        if save_btn:
            # Priority 1: File Upload
            if uploaded_file is not None:
                try:
                    # Read bytes and decode to string
                    content_to_save = uploaded_file.getvalue().decode("utf-8")
                    source_name = uploaded_file.name
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
            
            # Priority 2: Manual Text (if no file is uploaded)
            elif manual_text.strip():
                content_to_save = manual_text
                source_name = "manual_input"

            # Save to Backend
            if content_to_save:
                db_instance.add_document(content_to_save, topic_tag, source_name)
                st.success(f"✅ Knowledge added successfully from: **{source_name}**")
                
                # Force a rerun to update the topic list in the Sidebar immediately
                import time
                time.sleep(1) # Small delay to let user see the success message
                st.rerun()
            else:
                st.warning("⚠️ Please provide text or upload a file before saving.")

    st.divider()

    # --- Execution Area (Workspace) ---
    st.subheader("Workspace")
    user_prompt = st.text_area("Enter your prompt:", height=100)
    
    if st.button("🚀 Execute Pipeline", type="primary"):
        # Validation: Check if pipeline has steps
        if not config["pasos"]: # Note: Ensure this key matches what sidebar returns ('pasos' or 'pipeline_steps')
            st.error("Please add at least one model in the sidebar configuration.")
            return

        if not user_prompt:
            st.warning("Please write a prompt first.")
            return

        # 1. RAG Retrieval Phase
        # Query the DB for context relevant to the prompt and selected topics
        # Note: Ensure key matches sidebar config ('temas_rag' or 'rag_topics')
        # Assuming 'temas_rag' based on previous sidebar code.
        temas_seleccionados = config.get("temas_rag", []) 
        
        retrieved_context = db_instance.query_db(user_prompt, temas_seleccionados)
        
        current_input = user_prompt
        
        if retrieved_context:
            st.info(f"💡 **RAG Active:** Context found in {len(temas_seleccionados)} topics.")
            with st.expander("View Retrieved Context"):
                st.caption(retrieved_context[:1000] + "..." if len(retrieved_context) > 1000 else retrieved_context)
            
            # Augment the prompt
            current_input = f"Context:\n{retrieved_context}\n\nQuestion/Instruction: {user_prompt}"

        # 2. Sequential Model Execution
        with st.status("Processing Pipeline...", expanded=True) as status:
            
            # Assuming config key is 'pasos' based on previous sidebar code
            pipeline_steps = config.get("pasos", [])
            
            for i, step in enumerate(pipeline_steps):
                status.write(f"▶️ **Step {i+1}:** Running {step['model_id']}...")
                
                try:
                    output = execute_pipeline(step, current_input)
                    
                    st.markdown(f"**Output Step {i+1} ({step['task']}):**")
                    st.success(output)
                    
                    current_input = output
                    
                except Exception as e:
                    st.error(f"Error in step {i+1}: {str(e)}")
                    status.update(label="Execution Failed", state="error")
                    return
            
            status.update(label="Pipeline Completed Successfully!", state="complete", expanded=False)