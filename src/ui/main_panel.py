import streamlit as st
from src.backend.model_engine import execute_pipeline

def render_main_panel(db_instance, config):
    """
    Renders the main workspace area with file upload capabilities.
    """
    st.title("🐍 pItAgorin")
    st.markdown("### AI Orchestrator & Local Knowledge Base")

    # --- Knowledge Ingestion Section ---
    with st.expander("📚 Feed Knowledge Base (Upload Data)", expanded=False):
        
        tab_manual, tab_upload = st.tabs(["✍️ Manual Text", "📁 Upload File"])
        
        content_to_save = ""
        source_name = "manual"
        
        with tab_manual:
            manual_text = st.text_area("Paste text content here:", height=150)
            
        with tab_upload:
            uploaded_file = st.file_uploader("Upload a document", type=["txt", "md"])

        # --- Layout for Metadata and Save Button ---
        col_meta, col_btn = st.columns([3, 1])
        
        with col_meta:
            # 1. Get existing topics from DB
            existing_topics = db_instance.get_topics()
            
            # 2. Prepare options (Add 'Create New' at the top)
            options = ["➕ Create New Topic..."] + existing_topics
            
            # 3. Render Dropdown
            selected_option = st.selectbox("Select Topic / Tag", options)
            
            # 4. Logic: Show text input ONLY if 'Create New' is selected
            if selected_option == "➕ Create New Topic...":
                topic_tag = st.text_input("Enter new topic name", "General")
            else:
                # Use the selected existing topic
                topic_tag = selected_option
                # We display it as disabled text just for visual confirmation (optional)
                st.info(f"Selected Topic: **{topic_tag}**")
            
        with col_btn:
            st.write("") # Spacer
            st.write("") 
            # We add extra spacing to align button with the inputs
            st.write("")
            save_btn = st.button("💾 Save to DB", use_container_width=True)

        # --- Saving Logic ---
        if save_btn:
            if uploaded_file is not None:
                try:
                    content_to_save = uploaded_file.getvalue().decode("utf-8")
                    source_name = uploaded_file.name
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
            
            elif manual_text.strip():
                content_to_save = manual_text
                source_name = "manual_input"

            if content_to_save:
                # Use the determined 'topic_tag' variable
                db_instance.add_document(content_to_save, topic_tag, source_name)
                st.success(f"✅ Knowledge added to **{topic_tag}** from: {source_name}")
                
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.warning("⚠️ Please provide text or upload a file before saving.")

    st.divider()

    # --- Execution Area ---
    st.subheader("Workspace")
    user_prompt = st.text_area("Enter your prompt:", height=100)
    
    if st.button("🚀 Execute Pipeline", type="primary"):
        if not config["pasos"]:
            st.error("Please add at least one model in the sidebar configuration.")
            return

        if not user_prompt:
            st.warning("Please write a prompt first.")
            return

        temas_seleccionados = config.get("temas_rag", []) 
        
        retrieved_context = db_instance.query_db(user_prompt, temas_seleccionados)
        current_input = user_prompt
        
        if retrieved_context:
            st.info(f"💡 **RAG Active:** Context found in {len(temas_seleccionados)} topics.")
            with st.expander("View Retrieved Context"):
                st.caption(retrieved_context[:1000] + "..." if len(retrieved_context) > 1000 else retrieved_context)
            
            current_input = f"Context:\n{retrieved_context}\n\nQuestion/Instruction: {user_prompt}"

        with st.status("Processing Pipeline...", expanded=True) as status:
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