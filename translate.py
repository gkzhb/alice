from typing import List, Tuple, Optional, Any
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
        docs = chunk_doc(doc)

    with open(f"{output}.json", "w", encoding="utf-8") as f:
        content = {
            "file": input,
            "chunks": [doc.content for doc in docs],
        }
        f.write(json.dumps(content, ensure_ascii=False))
        return content


async def process_chunks(doc_list, output_file, log_file):
    semaphore = asyncio.Semaphore(5)  # Limit concurrent tasks

    async def process_one(idx, doc, prev_doc):
        async with semaphore:
            try:
                resp = await run_translate(doc, prev_doc)
                return (idx, doc, resp, prev_doc)
            except Exception as e:
                print(f"Error in process_one for chunk {idx}: {str(e)}")
                return (idx, doc, None, prev_doc)

    tasks = [
        process_one(idx, doc, doc_list["chunks"][idx - 1] if idx > 0 else "")
        for idx, doc in enumerate(doc_list["chunks"])
    ]

    # Process results as they complete but maintain order
    results: List[Optional[Tuple[int, str, Any, str]]] = [None] * len(tasks)
    for future in asyncio.as_completed(tasks):
        try:
            result = await future
            if not isinstance(result, (tuple, list)) or len(result) != 4:
                raise ValueError(f"Invalid result format: {result}")
            idx, doc, resp, prev_doc = result
            results[idx] = (idx, doc, resp, prev_doc)
        except Exception as e:
            print(f"Error processing task result: {str(e)}")
            # Skip this result as we can't determine its index

    # Write all results in original order
    with (
        open(output_file, "w", encoding="utf-8") as f,
        open(log_file, "w", encoding="utf-8") as log,
    ):
        for result in results:
            if (
                result is None
                or not isinstance(result, (tuple, list))
                or len(result) != 4
                or result[2] is None
            ):
                continue  # Skip invalid or failed tasks
            idx, doc, resp, prev_doc = result
            f.write(resp.content.translated + "\n")
            log.write(
                json.dumps(
                    {
                        "index": idx,
                        "doc": doc,
                        "prev_doc": prev_doc,
                        "translated": resp.content.translated,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
        # Single flush at the end
        f.flush()
        log.flush()


async def main():
    doc_list = chunk_file("./data/input/antinet-zk.txt", "./data/output/antinet-chunks")
    print(f"chunk list len:{len(doc_list['chunks'])}")
    if len(doc_list["chunks"]) < 10:
        print("chunk failed")
        return

    output_file = "./data/output/antinet-translated2.txt"
    log_file = "./data/output/antinet-translated.log"

    await process_chunks(doc_list, output_file, log_file)


if __name__ == "__main__":
    asyncio.run(main())
