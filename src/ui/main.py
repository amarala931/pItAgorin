import streamlit as st
from src.backend.model_engine import execute_pipeline

def render_main_panel(db_instance, config):
    """
    Renders the main workspace area.
    
    Args:
        db_instance: The KnowledgeBase object.
        config (dict): The configuration returned by the sidebar.
    """
    # Header with the project name
    st.title("🐍 pItAgorin")
    st.markdown("### AI Orchestrator & Local Knowledge Base")

    # --- Knowledge Ingestion Section (Expander) ---
    with st.expander("📚 Feed Knowledge Base (Upload Data)"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Input for raw text and topic tagging
            input_text = st.text_area("Text content to memorize", height=100)
            topic_tag = st.text_input("Topic / Tag", "General")
            
        with col2:
            st.write("") # Spacer
            st.write("") # Spacer
            if st.button("💾 Save to DB"):
                if input_text:
                    # Call backend to save vector embeddings
                    db_instance.add_document(input_text, topic_tag)
                    st.success("Saved successfully!")
                    # Rerun to update the topic list in sidebar
                    st.rerun()
                else:
                    st.warning("Please enter text.")

    st.divider()

    # --- Execution Area ---
    st.subheader("Workspace")
    user_prompt = st.text_area("Enter your prompt:", height=100)
    
    if st.button("🚀 Execute Pipeline", type="primary"):
        # Validation: Check if pipeline has steps
        if not config["pipeline_steps"]:
            st.error("Please add at least one model in the sidebar configuration.")
            return

        if not user_prompt:
            st.warning("Please write a prompt first.")
            return

        # 1. RAG Retrieval Phase
        # Query the DB for context relevant to the prompt and selected topics
        retrieved_context = db_instance.query_db(user_prompt, config["rag_topics"])
        
        current_input = user_prompt
        
        if retrieved_context:
            st.info("💡 Relevant context found in Knowledge Base.")
            with st.expander("View Context"):
                st.write(retrieved_context)
            
            # Augment the prompt with the retrieved context
            current_input = f"Context:\n{retrieved_context}\n\nQuestion/Instruction: {user_prompt}"

        # 2. Sequential Model Execution
        # We use st.status to show a cool loading state
        with st.status("Processing Pipeline...", expanded=True) as status:
            
            for i, step in enumerate(config["pipeline_steps"]):
                status.write(f"▶️ **Step {i+1}:** Running {step['model_id']}...")
                
                try:
                    # Execute the specific model step
                    output = execute_pipeline(step, current_input)
                    
                    # Display intermediate result
                    st.markdown(f"**Output Step {i+1} ({step['task']}):**")
                    st.success(output)
                    
                    # Chain: Output of this step becomes input for the next
                    current_input = output
                    
                except Exception as e:
                    st.error(f"Error in step {i+1}: {str(e)}")
                    status.update(label="Execution Failed", state="error")
                    return
            
            status.update(label="Pipeline Completed Successfully!", state="complete", expanded=False)