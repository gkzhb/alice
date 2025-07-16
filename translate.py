import json
from agno.storage.sqlite import SqliteStorage
from agno.agent import AgentKnowledge
from agno.vectordb.lancedb import LanceDb
from agno.vectordb.search import SearchType
from agno.utils.pprint import pprint_run_response
from alice.agents.translater import TranslaterAgent
from alice.model.llm import ds_chat_model
from alice.model.embedding import bge_embedder
from alice.chunkings.document import chunk_doc

storage = SqliteStorage(
    table_name="translater_result",
    db_file= "data/dev/translater.db",
)
vector_db = LanceDb(
    table_name="translate_glossary",
    uri="data/dev/lancedb_translater",
    embedder=bge_embedder,
    search_type=SearchType.keyword
)
kb = AgentKnowledge(vector_db=vector_db)
translater = TranslaterAgent(ds_chat_model, storage, kb)

def run_translate(text:str, ctx: str):
    glossary = """
terms:
  - original: "Antinet"
    translation: "Antinet"
    definition: "一种卡片盒笔记的方法 Antinet"
    context: "本书作者提出了 Antinet 卡片盒笔记法"
"""
    # kb.load_text(glossary)
    # text = """
# The Who And Why Of The Antinet\n\n\n\t\t\tIn the early days of writing this book, I recorded a podcast every day.23 In the podcast, I mainly discussed items related to what I was discovering about the Antinet.\n
# """
    resp = translater.run(glossary, ctx, text)
    pprint_run_response(resp)
    return resp
    
def chunk_file(input: str, output: str):
    with open(input) as f:
        doc = f.read()
        docs = chunk_doc(doc)

    with open(f'{output}.json', 'w', encoding='utf-8') as f:
        content = {
            "file": input,
            "chunks": [doc.content for doc in docs],
        }
        f.write(json.dumps(content, ensure_ascii=False))
        return content

doc_list = chunk_file('./data/input/antinet-zk.txt', './data/output/antinet-chunks')
print(f'chunk list len:{len(doc_list["chunks"])}')
if len(doc_list['chunks']) < 10:
    print('chunk failed')
    exit(0)

output_file = './data/output/antinet-translated2.txt'
# jsonl log file to preserve running info
log_file = './data/output/antinet-translated.log'
# 清空或创建文件
# with open(output_file, 'w', encoding='utf-8') as f:
#     pass

# previous doc content
prev_doc = ""
with open(output_file, 'a', encoding='utf-8') as f, open(log_file, 'a', encoding='utf-8') as log:
    for idx, doc in enumerate(doc_list['chunks']):
        resp = run_translate(doc, prev_doc)
        # 将当前翻译结果追加到文件
        f.write(resp.content.translated + '\n')
        log.write(json.dumps({
            "index": idx,
            "doc": doc,
            "prev_doc": prev_doc,
            "translated": resp.content.translated,
            }, ensure_ascii=False) + '\n')

        prev_doc = doc[-1200:]
        # flush written files
        f.flush()
        log.flush()
