import streamlit as st
from src.backend.model_engine import execute_pipeline

def render_main_panel(db_instance, config, logo_img=None):
    
    # Cabecera con columnas para poner logo pequeño y título
    c1, c2 = st.columns([1, 5])
    with c1:
        if logo_img:
            st.image(logo_img, width=80)
        else:
            st.write("🤖")
    with c2:
        st.title("pItAgorin")
        st.caption("Orchestrating the Wisdom of AI")

    # --- Knowledge Ingestion Section ---
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

    # --- WORKSPACE ---
    st.subheader("Workspace")
    user_prompt = st.text_area("Enter your main instruction/prompt:", height=100)

    # --- Advanced Prompt Configuration ---
    with st.expander("⚙️ Advanced Prompt Engineering", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            role = st.text_input("🎭 Role / Persona")
            audience = st.text_input("🎯 Target Audience")
            tone = st.selectbox("🎨 Tone & Style", ["Default", "Formal", "Concise", "Creative", "Socratic", "ELI5"])
        with c2:
            output_format = st.selectbox("📝 Output Format", ["Text", "Markdown Table", "Bullet Points", "JSON", "Code"])
            structure_override = st.text_input("Custom structure:")
            active_constraints = st.multiselect("🚫 Negative Constraints", ["No preambles", "No apologies", "No passive voice", "No jargon"])
            negative_context = st.text_input("Specific Avoidance")

    # --- Execution Logic ---
    if st.button("🚀 Execute Pipeline", type="primary"):
        if not config.get("pipeline_steps"):
            st.error("Please configure the model pipeline in the sidebar first.")
            return
        if not user_prompt:
            st.warning("Main prompt is required.")
            return

        # Mega-Prompt Construction
        system_instruction = []
        if role: system_instruction.append(f"ROLE: Act as a {role}.")
        if audience: system_instruction.append(f"AUDIENCE: Adapt response for {audience}.")
        if tone and tone != "Default": system_instruction.append(f"TONE: {tone}.")
        
        final_format = structure_override if structure_override else output_format
        if final_format != "Text": system_instruction.append(f"FORMAT: Provide output as {final_format}.")
        
        all_constraints = active_constraints.copy()
        if negative_context: all_constraints.append(negative_context)
        if all_constraints: system_instruction.append(f"CONSTRAINTS (AVOID): {', '.join(all_constraints)}.")

        meta_prompt = "\n".join(system_instruction)
        temas_seleccionados = config.get("rag_topics", []) 
        retrieved_context = db_instance.query_db(user_prompt, temas_seleccionados)
        
        full_input_package = ""
        if meta_prompt: full_input_package += f"--- SYSTEM INSTRUCTIONS ---\n{meta_prompt}\n\n"
        if retrieved_context:
            st.info(f"💡 RAG Active: {len(temas_seleccionados)} topics.")
            full_input_package += f"--- KNOWLEDGE BASE CONTEXT ---\n{retrieved_context}\n\n"
        full_input_package += f"--- TASK ---\n{user_prompt}"

        current_input = full_input_package
        
        with st.status("Processing Pipeline...", expanded=True) as status:
            pipeline_steps = config.get("pipeline_steps", [])
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
            status.update(label="Pipeline Completed!", state="complete", expanded=False)