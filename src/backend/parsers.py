import io
import pandas as pd
from pypdf import PdfReader
from docx import Document

def parse_uploaded_file(uploaded_file):
    """
    Detecta el tipo de archivo y extrae su texto.
    Retorna el texto extraído como string.
    """
    file_type = uploaded_file.name.split('.')[-1].lower()
    text = ""

    try:
        # 1. Archivos de Texto Plano y Markdown
        if file_type in ['txt', 'md']:
            text = uploaded_file.getvalue().decode("utf-8")

        # 2. Archivos PDF
        elif file_type == 'pdf':
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                # Extraemos texto y añadimos salto de línea
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # 3. Archivos Word (.docx)
        elif file_type == 'docx':
            doc = Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])

        # 4. Archivos CSV
        elif file_type == 'csv':
            # Leemos el CSV y lo convertimos a formato Markdown para que el LLM lo entienda mejor
            df = pd.read_csv(uploaded_file)
            text = df.to_markdown(index=False)

    except Exception as e:
        raise ValueError(f"Error parsing {file_type.upper()}: {str(e)}")

    return text