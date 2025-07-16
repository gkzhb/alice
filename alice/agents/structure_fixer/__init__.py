from pydantic import BaseModel
from typing import Type, TypeVar, Generic
from agno.agent import Agent
from agno.models.base import Model
from agno.utils.pprint import pprint_run_response
from alice.utils.agent import get_agent_id

T = TypeVar("T", bound=BaseModel)


class StructureFixerAgent(Generic[T]):
    name = "StructureFixer"
    version = "20250717-1"
    agent: Agent

    def __init__(self, model: Model, data_model: Type[T]):
        self.data_model = data_model
        system_prompt = (
            f"你是一个数据格式修复专家。你的任务是将模型的原始输出修复为符合 {data_model.__name__} 结构的数据。\n"
            "你需要分析原始输出，识别不符合规范的部分，并进行修正。\n"
            "返回结果必须严格遵循给定的格式。"
        )

        self.agent = Agent(
            model=model,
            name=self.name,
            agent_id=get_agent_id(self.name, self.version),
            system_message=system_prompt,
            response_model=data_model,
            use_json_mode=True,
        )

    async def arun(self, raw_output: str):
        user_prompt = (
            f"请将以下原始输出修复为符合 {self.data_model.__name__} 结构的数据:\n"
            f"原始输出:\n{raw_output}\n\n"
            "请分析并修复以下问题:\n"
            "1. 类型不匹配的字段\n"
            "2. 缺失的必填字段\n"
            "3. 格式不正确的数据\n"
            "4. 其他结构性问题"
        )

        resp = await self.agent.arun(user_prompt)

        if not isinstance(resp.content, self.data_model):
            print(f"[DEBUG] Invalid response format: {resp}")
            pprint_run_response(resp)
            raise ValueError(
                f"Response content must be {self.data_model.__name__}, got {type(resp.content)}. "
                f"Full response: {resp}"
            )

        return resp
