from agno.knowledge.website import WebsiteKnowledgeBase
from agno.vectordb.lancedb import LanceDb
from alice.model.embedding import bge_embedder

lance_db = LanceDb(
    table_name="doc",
    uri="data/dev/lancedb-agno",
    embedder=bge_embedder,
)

agno_kb = WebsiteKnowledgeBase(
    urls=["https://docs.agno.com/introduction"],
    # Number of links to follow from the seed URLs
    max_links=10,
    # Table name: ai.website_documents
    vector_db=lance_db,
)