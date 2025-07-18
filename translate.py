from typing import List, Tuple, Any, Coroutine
import json
import asyncio
from agno.storage.sqlite import SqliteStorage
from agno.agent import AgentKnowledge
from agno.vectordb.lancedb import LanceDb
from agno.vectordb.search import SearchType
from agno.utils.pprint import pprint_run_response
from alice.agents.translater import TranslaterAgent
from alice.model.llm import ds_chat_model
from alice.model.embedding import bge_embedder
from alice.chunkings.document import chunk_doc
from alice.utils.async_queue import AsyncTaskQueue

storage = SqliteStorage(
    table_name="translater_result",
    db_file="data/dev/translater.db",
)
vector_db = LanceDb(
    table_name="translate_glossary",
    uri="data/dev/lancedb_translater",
    embedder=bge_embedder,
    search_type=SearchType.keyword,
)
kb = AgentKnowledge(vector_db=vector_db)
translater = TranslaterAgent(ds_chat_model, storage, kb)


async def run_translate(text: str, ctx: str):
    glossary = """
terms:
  - original: "Antinet"
    translation: "Antinet"
    definition: "一种卡片盒笔记的方法 Antinet"
    context: "本书作者提出了 Antinet 卡片盒笔记法"
"""
    resp = await translater.arun(glossary, ctx, text)
    pprint_run_response(resp)
    return resp


def chunk_file(input: str, output: str):
    with open(input) as f:
        doc = f.read()
        docs = chunk_doc(doc, 4000)

    with open(f"{output}.json", "w", encoding="utf-8") as f:
        content = {
            "file": input,
            "chunks": [doc.content for doc in docs],
        }
        f.write(json.dumps(content, ensure_ascii=False))
        return content


async def process_chunks(doc_list, output_file, log_file):
    async def process_one(
        idx: int, doc: str, prev_doc: str
    ) -> Tuple[int, str, Any, str]:
        """处理单个文本块的翻译任务"""
        try:
            resp = await run_translate(doc, prev_doc)
            return (idx, doc, resp, prev_doc)
        except Exception as e:
            print(f"Error in process_one for chunk {idx}: {str(e)}")
            return (idx, doc, None, prev_doc)

    # 明确tasks列表类型
    tasks: List[Coroutine[Any, Any, Tuple[int, str, Any, str]]] = [
        process_one(idx, doc, doc_list["chunks"][idx - 1] if idx > 0 else "")
        for idx, doc in enumerate(doc_list["chunks"])
    ]

    with (
        open(output_file, "a", encoding="utf-8") as f,
        open(log_file, "a", encoding="utf-8") as log,
    ):
        # 后处理函数：写入文件
        def post_process(result):
            idx, doc, resp, prev_doc = result
            print("process output", idx)
            if resp is not None:
                f.write(resp.content.translated + "\n")
                log.write(
                    json.dumps(
                        {
                            "index": idx,
                            "doc": doc,
                            "prev_doc": prev_doc,
                            "translated": resp.content.translated,
                            "error": False,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            else:
                log.write(
                    json.dumps(
                        {
                            "index": idx,
                            "doc": doc,
                            "prev_doc": prev_doc,
                            "error": True,
                            "message": "Translation response is None",
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            return result

        # 使用AsyncTaskQueue执行任务
        queue = AsyncTaskQueue[Tuple[int, str, Any, str]](max_workers=10)
        for task in tasks:
            queue.add_task(task)
        await queue.run(post_process=post_process)


async def main():
    doc_list = chunk_file("./data/input/antinet-zk.txt", "./data/output/antinet-chunks")
    print(f"chunk list len:{len(doc_list['chunks'])}")
    if len(doc_list["chunks"]) < 10:
        print("chunk failed")
        return

    baes_file_name = "antinet-translated4"
    output_file = f"./data/output/{baes_file_name}.txt"
    log_file = f"./data/output/{baes_file_name}.log"

    await process_chunks(doc_list, output_file, log_file)


if __name__ == "__main__":
    asyncio.run(main())
