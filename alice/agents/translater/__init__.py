from pydantic import BaseModel, Field
from agno.agent import Agent, AgentKnowledge
from agno.models.base import Model
from agno.storage.base import Storage
from agno.utils.pprint import pprint_run_response
from alice.agents.structure_fixer import StructureFixerAgent
from alice.utils.agent import get_agent_id
from .prompt import translater_system_prompt, translater_user_prompt


class TranslateScript(BaseModel):
    translated: str = Field(..., description="翻译后文本")
    glossary: str = Field(..., description="翻译术语表")


class TranslaterAgent:
    name = "Translater"
    version = "20250714-1"
    agent: Agent
    fixer: StructureFixerAgent
    kb: AgentKnowledge

    def __init__(self, model: Model, storage: Storage, kb: AgentKnowledge):
        prompt = translater_system_prompt.get_prompt(
            {"original_language": "英文", "target_language": "中文"}
        )
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
        self.fixer = StructureFixerAgent(model, TranslateScript)

    async def arun(self, glossary: str, context: str, text: str):
        user_prompt = translater_user_prompt.get_prompt(
            {"glossary": glossary, "context": context, "text": text}
        )
        max_retries = 3
        retry_count = 0
        resp = None

        while retry_count <= max_retries:
            resp = await self.agent.arun(user_prompt)
            if isinstance(resp.content, TranslateScript):
                break

            print(
                f"[DEBUG] Invalid response format, attempting to retry ({retry_count + 1}/{max_retries})"
            )

            retry_count += 1
            if retry_count > max_retries:
                pprint_run_response(resp)
                raise ValueError(
                    f"Failed to translate after {max_retries} retries. "
                    f"Get type: {type(resp.content)}. "
                    f"Full response: {resp}"
                )

        if resp is None:
            raise RuntimeError("Unexpected error: response is None")

        glossary = resp.content.glossary
        if glossary:
            self.kb.load_text(glossary)
        return resp
