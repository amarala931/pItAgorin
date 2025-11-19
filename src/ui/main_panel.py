import streamlit as st
from src.backend.model_engine import execute_pipeline

def render_main_panel(db_instance, config):
    """
    Renders the main workspace area with Advanced Prompt Engineering capabilities.
    """
    st.title("🐍 pItAgorin")
    st.markdown("### AI Orchestrator & Local Knowledge Base")

    # --- 1. Knowledge Ingestion Section (Preserved) ---
    with st.expander("📚 Feed Knowledge Base (Upload Data)", expanded=False):
        tab_manual, tab_upload = st.tabs(["✍️ Manual Text", "📁 Upload File"])
        content_to_save = ""
        source_name = "manual"
        
        with tab_manual:
            manual_text = st.text_area("Paste text content here:", height=150)
        with tab_upload:
            uploaded_file = st.file_uploader("Upload a document", type=["txt", "md"])

        col_meta, col_btn = st.columns([3, 1])
        with col_meta:
            existing_topics = db_instance.get_topics()
            options = ["➕ Create New Topic..."] + existing_topics
            selected_option = st.selectbox("Select Topic / Tag", options)
            if selected_option == "➕ Create New Topic...":
                topic_tag = st.text_input("Enter new topic name", "General")
            else:
                topic_tag = selected_option
        
        with col_btn:
            st.write("","", "")
            save_btn = st.button("💾 Save to DB", use_container_width=True)

        if save_btn:
            if uploaded_file:
                try:
                    content_to_save = uploaded_file.getvalue().decode("utf-8")
                    source_name = uploaded_file.name
                except Exception as e:
                    st.error(f"Error: {e}")
            elif manual_text.strip():
                content_to_save = manual_text
                source_name = "manual_input"

            if content_to_save:
                db_instance.add_document(content_to_save, topic_tag, source_name)
                st.success(f"✅ Saved to **{topic_tag}**")
                import time
                time.sleep(1)
                st.rerun()

    st.divider()

    # --- 2. WORKSPACE & PROMPT ENGINEERING ---
    st.subheader("Workspace")

    # --- A. Main Task Input ---
    user_prompt = st.text_area("Enter your main instruction/prompt:", height=100, placeholder="e.g., Summarize the quarterly financial report...")

    # --- B. Advanced Prompt Configuration (New Section) ---
    with st.expander("⚙️ Advanced Prompt Engineering (Context & Constraints)", expanded=False):
        st.caption("Configure how the AI should think and respond.")
        
        c1, c2 = st.columns(2)
        
        with c1:
            # Rol / Persona
            role = st.text_input("🎭 Role / Persona", placeholder="e.g., Senior Data Scientist, Empathetic Teacher")
            
            # Audiencia Objetivo
            audience = st.text_input("🎯 Target Audience", placeholder="e.g., Executives, 5-year old, Developers")
            
            # Tono y Estilo
            tone_options = ["Default", "Formal & Professional", "Concise & Direct", "Creative & Enthusiastic", "Socratic (Ask Questions)", "ELI5 (Simple)"]
            tone = st.selectbox("🎨 Tone & Style", tone_options)

        with c2:
            # Formato de Salida
            format_options = ["Text (Default)", "Markdown Table", "Bullet Points", "JSON", "Python Code", "Executive Summary", "Step-by-Step Guide"]
            output_format = st.selectbox("📝 Output Format", format_options)
            
            # Granular Structure (Optional override)
            structure_override = st.text_input("Or define custom structure:", placeholder="e.g., 1. Title, 2. Analysis, 3. Conclusion")

            # Restricciones / Contexto Negativo
            constraints_options = [
                "No preambles ('Here is the...')", 
                "No AI apologies ('As an AI...')", 
                "No passive voice", 
                "No jargon"
            ]
            active_constraints = st.multiselect("🚫 Negative Constraints", constraints_options)
            
            # Specific Negative Context
            negative_context = st.text_input("Specific Avoidance", placeholder="e.g., Do not mention competitors, Don't use Markdown")

    # --- 3. Execution Logic ---
    if st.button("🚀 Execute Pipeline", type="primary"):
        
        # Validation
        if not config.get("pipeline_steps"):
            st.error("Please configure the model pipeline in the sidebar first.")
            return
        if not user_prompt:
            st.warning("Main prompt is required.")
            return

        # --- PROMPT ASSEMBLY (The "Mega-Prompt" Builder) ---
        # We construct a structured prompt invisible to the user but seen by the AI
        system_instruction = []
        
        if role: system_instruction.append(f"ROLE: Act as a {role}.")
        if audience: system_instruction.append(f"AUDIENCE: Adapt response for {audience}.")
        
        if tone and tone != "Default": system_instruction.append(f"TONE: {tone}.")
        
        # Format Logic
        final_format = structure_override if structure_override else output_format
        if final_format != "Text (Default)":
             system_instruction.append(f"FORMAT: Provide output as {final_format}.")

        # Constraints Logic
        all_constraints = active_constraints.copy()
        if negative_context: all_constraints.append(negative_context)
        if all_constraints:
            system_instruction.append(f"CONSTRAINTS (DO NOT DO): {', '.join(all_constraints)}.")

        # Join all meta-instructions
        meta_prompt = "\n".join(system_instruction)

        # --- RAG Retrieval ---
        temas_seleccionados = config.get("rag_topics", []) 
        retrieved_context = db_instance.query_db(user_prompt, temas_seleccionados)
        
        # --- Final Input Construction ---
        # 1. Meta-Instructions (Role, Tone, etc.)
        # 2. Context (RAG)
        # 3. The User's Actual Question
        
        full_input_package = ""
        
        if meta_prompt:
            full_input_package += f"--- SYSTEM INSTRUCTIONS ---\n{meta_prompt}\n\n"
            
        if retrieved_context:
            st.info(f"💡 **RAG Active:** Context found in {len(temas_seleccionados)} topics.")
            with st.expander("View Retrieved Context"):
                st.caption(retrieved_context[:800] + "...")
            full_input_package += f"--- KNOWLEDGE BASE CONTEXT ---\n{retrieved_context}\n\n"
            
        full_input_package += f"--- TASK ---\n{user_prompt}"

        # --- Execution Loop ---
        current_input = full_input_package
        
        with st.status("Processing Pipeline...", expanded=True) as status:
            pipeline_steps = config.get("pipeline_steps", [])
            
            for i, step in enumerate(pipeline_steps):
                status.write(f"▶️ **Step {i+1}:** Running {step['model_id']}...")
                try:
                    # If it's the first step, use the full engineered prompt.
                    # For subsequent steps (e.g., translation), we might just want the text, 
                    # but carrying context is usually safer in generic pipelines.
                    output = execute_pipeline(step, current_input)
                    
                    st.markdown(f"**Output Step {i+1} ({step['task']}):**")
                    st.success(output)
                    
                    current_input = output
                except Exception as e:
                    st.error(f"Error in step {i+1}: {str(e)}")
                    status.update(label="Execution Failed", state="error")
                    return
            
            status.update(label="Pipeline Completed Successfully!", state="complete", expanded=False)