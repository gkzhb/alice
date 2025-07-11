from agno.models.litellm import LiteLLM

ds_chat_model = LiteLLM(
    id='volcengine/deepseek-v3-250324',
    name='DeepSeek V3',
)

ds_reasoning_model = LiteLLM(
    id='volcengine/deepseek-r1-250528',
    name='DeepSeek R1',
)