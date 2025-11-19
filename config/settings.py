import os

# Project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "chroma_store")

# Path where the database will be stored (inside the `data` folder)
DB_PATH = os.path.join(BASE_DIR, "data", "chroma_store")

# Catalog of available models
MODEL_CATALOG = {
    "Assistant (Google Flan-T5)": {"task": "text2text-generation", "model_id": "google/flan-t5-base"},
    "Translator EN-ES": {"task": "translation_en_to_es", "model_id": "Helsinki-NLP/opus-mt-en-es"},
    "Summarizer": {"task": "summarization", "model_id": "sshleifer/distilbart-cnn-12-6"}
}

# Database connection configurations
sql_user = os.getenv("DB_SQL_USER", "root")
sql_pass = os.getenv("DB_SQL_PASS", "")
sql_host = os.getenv("DB_SQL_HOST", "localhost")
sql_port = os.getenv("DB_SQL_PORT", "3306")
sql_db   = os.getenv("DB_SQL_NAME", "test_db")

sql_connection_string = f"mysql+pymysql://{sql_user}:{sql_pass}@{sql_host}:{sql_port}/{sql_db}"

DATABASES = {
"""
    # 1. Base de datos SQL Corporativa (Cargada desde .env)
    "SQL Corporativo (Prod)": {
        "type": "sql",
        "connection_string": sql_connection_string
    },
    
    # 2. MongoDB Analytics (Cargada desde .env)
    "Mongo Analytics": {
        "type": "mongo",
        "connection_string": os.getenv("DB_MONGO_URI", "mongodb://localhost:27017/"),
        "default_db": os.getenv("DB_MONGO_DEFAULT_DB", "admin")
    },
    
    # 3. SQLite Local (Para pruebas rápidas, basado en archivo local)
    "SQLite Local (Demo)": {
        "type": "sql",
        "connection_string": f"sqlite:///{os.path.join(BASE_DIR, 'data', 'demo.db')}"
    }
    """
}