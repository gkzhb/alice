from pydantic import BaseModel, Field
from agno.agent import Agent, RunResponse
from alice.model.llm import ds_chat_model
from rich.prompt import Prompt

class TranslateScript(BaseModel):
    translatedText: str = Field(..., description="翻译后文本")
    glossary: str = Field(..., description="翻译术语表")
    
    
json_mode_agent = Agent(
    model=ds_chat_model,
    description="将给定文本从英文翻译为中文",
    response_model=TranslateScript,
    use_json_mode=True,
)

text = Prompt.ask("待翻译的英文文本")

json_mode_agent.print_response(text, stream=True, stream_intermediate_steps=True, show_message=False)