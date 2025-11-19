import os

# Project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path where the database will be stored (inside the `data` folder)
DB_PATH = os.path.join(BASE_DIR, "data", "chroma_store")

# Catalog of available models
MODEL_CATALOG = {
    "Assistant (Google Flan-T5)": {"task": "text2text-generation", "model_id": "google/flan-t5-base"},
    "Translator EN-ES": {"task": "translation_en_to_es", "model_id": "Helsinki-NLP/opus-mt-en-es"},
    "Summarizer": {"task": "summarization", "model_id": "sshleifer/distilbart-cnn-12-6"}
}