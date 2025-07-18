from agno.document.base import Document
from agno.document.chunking.fixed import FixedSizeChunking


def chunk_doc(doc: str, chunk_size: int):
    document = Document(content=doc)
    chunking_strategy = FixedSizeChunking(chunk_size=chunk_size)
    chunks = chunking_strategy.chunk(document)
    return chunks
