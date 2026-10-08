import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# El archivo con secretos está en .venv/.env en este proyecto.
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)

uri = os.getenv("MONGODB_URI")
database_name = os.getenv("MONGODB_DB")

if not uri:
    raise RuntimeError("Faltan MONGODB_URI en el archivo .env")
if not database_name:
    raise RuntimeError("Faltan MONGODB_DB en el archivo .env")

client = MongoClient(
    uri,
    server_api=ServerApi("1"),
    serverSelectionTimeoutMS=5000,
)

db = client[database_name]