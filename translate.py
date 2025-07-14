from agno.storage.sqlite import SqliteStorage
from agno.utils.pprint import pprint_run_response
from alice.agents.translater import TranslaterAgent
from alice.model.llm import ds_chat_model

storage = SqliteStorage(
    table_name="translater_result",
    db_file= "data/dev/translater.db",
)
translater = TranslaterAgent(ds_chat_model, storage)

def run_translate():
    glossary = """
"""
    text = """
The Who And Why Of The Antinet\n\n\n\t\t\tIn the early days of writing this book, I recorded a podcast every day.23 In the podcast, I mainly discussed items related to what I was discovering about the Antinet.\n
"""
    resp = translater.run(glossary, "", text)
    pprint_run_response(resp)
    print(f"Content Type:{resp.content_type} {resp.content}")
    print(f"\n###翻译结果：\n{resp.content.translated}\n\n###术语表：\n{resp.content.glossary}")
    
run_translate()