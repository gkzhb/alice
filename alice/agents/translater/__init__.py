from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.base import Model
from agno.storage.base import Storage
from alice.utils.agent import get_agent_id
from .prompt import translater_system_prompt, translater_user_prompt

class TranslateScript(BaseModel):
    translated: str = Field(..., description="翻译后文本")
    glossary: str = Field(..., description="翻译术语表")

class TranslaterAgent:
    name = 'Translater'
    version = '20250714-1'
    agent: Agent
    def __init__(self, model: Model, storage: Storage):
        prompt = translater_system_prompt.get_prompt({"original_language": "英文", "target_language": "中文"})
        self.agent = Agent(
            model=model,
            name=self.name,
            agent_id=get_agent_id(self.name, self.version),
            system_message=prompt,
            storage=storage,
            response_model=TranslateScript,
            use_json_mode=True,
            # debug_mode=True,
        )
    
    def run(self, glossary: str, context: str, text: str):
        user_prompt = translater_user_prompt.get_prompt({"glossary":glossary, "context": context, "text": text})
        resp = self.agent.run(user_prompt)
        return resp