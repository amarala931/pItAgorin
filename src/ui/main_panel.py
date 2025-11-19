import streamlit as st
import time
import json
from config.settings import DATABASES
from src.backend.model_engine import execute_pipeline
from src.backend.parsers import parse_uploaded_file
from src.backend.db_connectors import fetch_database_data

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
        
        tab_manual, tab_upload, tab_db = st.tabs(["✍️ Manual Text", "📁 Upload File", "🗄️ Databases"])
        content_to_save = ""
        source_name = "manual"
        
        with tab_manual:
            manual_text = st.text_area("Paste text content here:", height=150)
            
        with tab_upload:
            uploaded_file = st.file_uploader(
                "Upload a document", 
                type=["txt", "md", "pdf", "docx", "csv", "json", "yaml", "yml", "xml"]
            )
        with tab_db:
            if not DATABASES:
                st.warning("No databases configured in settings.py")
            else:
                col_conn, col_params = st.columns([1, 2])
                
                with col_conn:
                    selected_db_name = st.selectbox("Select Connection", list(DATABASES.keys()))
                    db_config = DATABASES[selected_db_name]
                    st.caption(f"Type: **{db_config['type'].upper()}**")

                query_params = {}
                
                with col_params:
                    if db_config['type'] == 'sql':
                        sql_query = st.text_area("SQL Query", "SELECT * FROM users LIMIT 5", height=100)
                        query_params["query"] = sql_query
                        source_name = f"SQL: {selected_db_name}"
                        
                    elif db_config['type'] == 'mongo':
                        c1, c2 = st.columns(2)
                        coll = c1.text_input("Collection Name")
                        limit = c2.number_input("Limit rows", 1, 100, 10)
                        filt = st.text_area("Filter (JSON)", "{}", height=68)
                        
                        query_params = {
                            "collection": coll,
                            "limit": limit,
                            "filter_json": filt,
                            # Opcional: permitir sobreescribir la DB
                            "db_name": db_config.get("default_db") 
                        }
                        source_name = f"Mongo: {selected_db_name}.{coll}"
                
                # Botón de vista previa para verificar conexión
                if st.button("Test Connection & Preview Data"):
                    try:
                        preview = fetch_database_data(db_config, query_params)
                        st.code(preview[:500] + "..." if len(preview) > 500 else preview, language="json")
                    except Exception as e:
                        st.error(f"Connection failed: {e}")

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
            # Priority 1: Database (Si estamos en esa pestaña activa sería ideal, 
            # pero aquí verificamos si hay configuración de DB lista para ejecutar)
            # Para simplificar, verificaremos flag o si venimos de un estado específico.
            # OJO: Como tenemos 3 fuentes, lo mejor es usar content_to_save como variable única.
            
            # LÓGICA DE PRIORIDAD ACTUALIZADA:
            try:
                # CASO 1: Archivo
                if uploaded_file:
                    content_to_save = parse_uploaded_file(uploaded_file)
                    source_name = uploaded_file.name
                
                # CASO 2: SQL/Mongo (Verificamos si estamos intentando guardar desde DB)
                # Una forma robusta es comprobar si los inputs de DB tienen datos y no hay archivo
                elif selected_db_name and db_config:
                    # Ejecutamos la consulta REAL para guardar
                    # Nota: Esto es una simplificación. En una UI compleja usaríamos st.session_state para saber qué tab está activo.
                    # Asumimos que si no hay archivo ni texto manual, el usuario quiere la DB.
                    if not manual_text.strip() and not uploaded_file:
                         with st.spinner("Fetching data from DB..."):
                            content_to_save = fetch_database_data(db_config, query_params)
                
                # CASO 3: Texto Manual
                elif manual_text.strip():
                    content_to_save = manual_text
                    source_name = "manual_input"

            except Exception as e:
                st.error(f"Error importing data: {e}")
                content_to_save = None

            # Guardado final
            if content_to_save:
                db_instance.add_document(content_to_save, topic_tag, source_name)
                st.success(f"✅ Added to **{topic_tag}** from **{source_name}**")
                st.session_state["trigger_input_reset"] = True
                time.sleep(0.5)
                st.rerun()
            else:
                if not content_to_save:
                    st.warning("⚠️ No content generated. Check your inputs or query results.")

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