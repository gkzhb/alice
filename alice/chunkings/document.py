from agno.document.base import Document
from agno.document.chunking.document import DocumentChunking
from agno.document.chunking.fixed import FixedSizeChunking

def chunk_doc(doc: str):
    document = Document(content=doc)
    chunking_strategy = FixedSizeChunking(chunk_size=1000)
    chunks = chunking_strategy.chunk(document)
    return chunks
