from pydantic import BaseModel, Field
from agno.agent import Agent, AgentKnowledge
from agno.models.base import Model
from agno.storage.base import Storage
from agno.utils.pprint import pprint_run_response
from alice.utils.agent import get_agent_id
from .prompt import translater_system_prompt, translater_user_prompt

class TranslateScript(BaseModel):
    translated: str = Field(..., description="翻译后文本")
    glossary: str = Field(..., description="翻译术语表")

class TranslaterAgent:
    name = 'Translater'
    version = '20250714-1'
    agent: Agent
    kb: AgentKnowledge
    def __init__(self, model: Model, storage: Storage, kb: AgentKnowledge):
        prompt = translater_system_prompt.get_prompt({"original_language": "英文", "target_language": "中文"})
        self.kb = kb
        self.agent = Agent(
            model=model,
            name=self.name,
            agent_id=get_agent_id(self.name, self.version),
            system_message=prompt,
            storage=storage,
            response_model=TranslateScript,
            # use_json_mode=True,
            knowledge=kb,
            search_knowledge=True,
            # memory=memory,
            # debug_mode=True,
        )
    
    def run(self, glossary: str, context: str, text: str):
        user_prompt = translater_user_prompt.get_prompt({"glossary":glossary, "context": context, "text": text})
        resp = self.agent.run(user_prompt)
        if not isinstance(resp.content, TranslateScript):
            # 调试用：打印完整响应以便排查问题
            print(f"[DEBUG] Invalid response format: {resp}")
            pprint_run_response(resp)
            raise ValueError(
                f"Response content must be a dictionary, got {type(resp.content)}. "
                f"Full response: {resp}"
            )
        glossary = resp.content.glossary
        # translated_text = resp.content.translated
        if glossary:
            self.kb.load_text(glossary)
        return resp