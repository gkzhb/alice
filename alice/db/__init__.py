from agno.vectordb.lancedb import LanceDb
from alice.model.embedding import bge_embedder

sqlite_db_path = "data/dev/sessions.db"

lance_db = LanceDb(
    table_name="recipes",
    uri="data/dev/lancedb",
    embedder=bge_embedder,
)