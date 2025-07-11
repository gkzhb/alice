import os
from agno.embedder.openai import OpenAIEmbedder

bge_embedder = OpenAIEmbedder(
    id='BAAI/bge-m3',
    dimensions=1024,
    api_key=os.getenv('SILICONFLOW_API_KEY'),
    base_url='https://api.siliconflow.cn/v1',
)