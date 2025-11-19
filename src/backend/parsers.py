import io
import json
import yaml
import xml.dom.minidom
import pandas as pd
from pypdf import PdfReader
from docx import Document

def parse_uploaded_file(uploaded_file):
    """
    Detecta el tipo de archivo y extrae su texto formateado.
    """
    # Obtenemos la extensión y normalizamos a minúsculas
    file_type = uploaded_file.name.split('.')[-1].lower()
    text = ""

    try:
        # --- TEXTO PLANO ---
        if file_type in ['txt', 'md']:
            text = uploaded_file.getvalue().decode("utf-8")

        # --- DOCUMENTOS ---
        elif file_type == 'pdf':
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        elif file_type == 'docx':
            doc = Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])

        # --- DATOS ESTRUCTURADOS (TABLAS) ---
        elif file_type == 'csv':
            df = pd.read_csv(uploaded_file)
            text = df.to_markdown(index=False)

        # --- DATOS SEMI-ESTRUCTURADOS (JSON, YAML, XML) ---
        elif file_type == 'json':
            # Leemos el JSON y lo volvemos a volcar con indentación para que la IA entienda la jerarquía
            data = json.load(uploaded_file)
            text = json.dumps(data, indent=2, ensure_ascii=False)

        elif file_type in ['yaml', 'yml']:
            data = yaml.safe_load(uploaded_file)
            text = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)

        elif file_type == 'xml':
            # Parseamos para validar y usamos toprettyxml para indentar correctamente
            dom = xml.dom.minidom.parse(uploaded_file)
            text = dom.toprettyxml()

    except Exception as e:
        raise ValueError(f"Error parsing {file_type.upper()}: {str(e)}")

    return text