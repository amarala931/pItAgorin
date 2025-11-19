import pandas as pd
from sqlalchemy import create_engine, text
from pymongo import MongoClient
import json

def fetch_database_data(db_config, query_params):
    """
    Orquesta la conexión y extracción de datos basándose en la configuración.
    Retorna un string formateado (JSON o Markdown).
    """
    db_type = db_config.get("type")
    uri = db_config.get("connection_string")

    if db_type == "sql":
        return _fetch_sql(uri, query_params["query"])
    elif db_type == "mongo":
        return _fetch_mongo(uri, db_config.get("default_db"), query_params)
    else:
        raise ValueError(f"Tipo de base de datos no soportado: {db_type}")

def _fetch_sql(uri, sql_query):
    """Conecta vía SQLAlchemy y usa Pandas para formatear."""
    try:
        engine = create_engine(uri)
        with engine.connect() as conn:
            # Pandas lee SQL y nos devuelve un DataFrame
            df = pd.read_sql(text(sql_query), conn)
            
            if df.empty:
                return "Consulta ejecutada correctamente pero no devolvió resultados."
            
            # Convertimos a JSON orientado a registros (fácil de leer para LLMs)
            return df.to_json(orient="records", indent=2)
    except Exception as e:
        raise ConnectionError(f"Error SQL: {str(e)}")

def _fetch_mongo(uri, default_db_name, params):
    """Conecta vía PyMongo."""
    try:
        client = MongoClient(uri)
        db_name = params.get("db_name") or default_db_name
        collection_name = params.get("collection")
        query_str = params.get("filter_json", "{}")
        limit = int(params.get("limit", 10))

        if not db_name or not collection_name:
            raise ValueError("Falta nombre de BD o Colección.")

        db = client[db_name]
        col = db[collection_name]

        # Parsear el filtro de string a diccionario
        try:
            query_filter = json.loads(query_str)
        except:
            query_filter = {}

        cursor = col.find(query_filter).limit(limit)
        results = list(cursor)

        if not results:
            return "Consulta ejecutada correctamente pero no devolvió resultados."

        # Convertir ObjectId y Datetimes a string para que sea serializable
        return json.dumps(results, indent=2, default=str)

    except Exception as e:
        raise ConnectionError(f"Error Mongo: {str(e)}")