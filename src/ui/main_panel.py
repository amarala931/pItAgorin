import streamlit as st
import time
from src.backend.model_engine import execute_pipeline
from src.backend.parsers import parse_uploaded_file

def render_main_panel(db_instance, config, logo_img=None):
    
    # --- 0. LÓGICA DE RESET ---
    if st.session_state.get("trigger_input_reset"):
        st.session_state["topic_pill_selection"] = None
        st.session_state["topic_input_field"] = "General"
        st.session_state["trigger_input_reset"] = False

    # --- 1. INICIALIZACIÓN DE ESTADO (CORRECCIÓN DEL ERROR) ---
    # Si la variable no existe en memoria, la creamos con el valor por defecto.
    # Esto reemplaza el uso de value="General" dentro del widget.
    if "topic_input_field" not in st.session_state:
        st.session_state["topic_input_field"] = "General"

    # --- HEADER ---
    st.title("pItAgorin")
    st.caption("Orchestrating the Wisdom of AI")

    # --- Knowledge Ingestion Section ---
# --- Knowledge Ingestion Section ---
    with st.expander("📚 Feed Knowledge Base (Upload Data)", expanded=False):
        
        tab_manual, tab_upload = st.tabs(["✍️ Manual Text", "📁 Upload File"])
        content_to_save = ""
        source_name = "manual"
        
        with tab_manual:
            manual_text = st.text_area("Paste text content here:", height=150)
            
        with tab_upload:
            # AÑADIDAS EXTENSIONES: json, yaml, yml, xml
            uploaded_file = st.file_uploader(
                "Upload a document", 
                type=["txt", "md", "pdf", "docx", "csv", "json", "yaml", "yml", "xml"]
            )

        # --- Lógica Unificada ---
        st.write("---")
        
        def _update_text_from_pill():
            # Callback: Pasa el valor de la píldora al input de texto
            if st.session_state.get("topic_pill_selection"):
                st.session_state["topic_input_field"] = st.session_state["topic_pill_selection"]

        col_input, col_btn = st.columns([4, 1])
        
        with col_input:
            # CORRECCIÓN AQUÍ: Eliminado parameter 'value="General"'
            # Ahora el widget se alimenta puramente de key="topic_input_field"
            topic_tag = st.text_input(
                "Topic / Tag", 
                key="topic_input_field",
                placeholder="Type new or select below..."
            )
            
            existing_topics = db_instance.get_topics()
            if existing_topics:
                st.caption("Quick Select Existing:")
                st.pills(
                    "Existing Topics",
                    options=existing_topics,
                    label_visibility="collapsed",
                    key="topic_pill_selection",
                    on_change=_update_text_from_pill,
                    selection_mode="single"
                )
        
        with col_btn:
            st.write("") 
            save_btn = st.button("💾 Save", use_container_width=True)

        # --- Saving Logic ---
        if save_btn:
            if uploaded_file:
                try:
                    # CAMBIO: Usamos la función del backend en lugar de leer a mano
                    content_to_save = parse_uploaded_file(uploaded_file)
                    source_name = uploaded_file.name
                except Exception as e:
                    st.error(f"Error: {e}")
            elif manual_text.strip():
                content_to_save = manual_text
                source_name = "manual_input"

            if content_to_save:
                db_instance.add_document(content_to_save, topic_tag, source_name)
                st.success(f"✅ Added to **{topic_tag}**")
                
                st.session_state["trigger_input_reset"] = True
                time.sleep(0.5)
                st.rerun()
            else:
                st.warning("⚠️ Provide text first.")

    st.divider()

    # --- WORKSPACE ---
    st.subheader("Workspace")
    user_prompt = st.text_area("Enter your main instruction/prompt:", height=100)

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

    if st.button("🚀 Execute Pipeline", type="primary"):
        if not config.get("pipeline_steps"):
            st.error("Sidebar config required.")
            return
        if not user_prompt:
            st.warning("Main prompt required.")
            return

        system_instruction = []
        if role: system_instruction.append(f"ROLE: Act as a {role}.")
        if audience: system_instruction.append(f"AUDIENCE: Adapt response for {audience}.")
        if tone and tone != "Default": system_instruction.append(f"TONE: {tone}.")
        
        final_format = structure_override if structure_override else output_format
        if final_format != "Text": system_instruction.append(f"FORMAT: Provide output as {final_format}.")
        
        all_constraints = active_constraints.copy()
        if negative_context: all_constraints.append(negative_context)
        if all_constraints: system_instruction.append(f"CONSTRAINTS: {', '.join(all_constraints)}.")

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