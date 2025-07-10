from agno.agent import Agent
from agno.models.litellm import LiteLLM
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    agent = Agent(
        model=LiteLLM(
            id='volcengine/deepseek-v3-250324',
            name='DeepSeek V3',
        ),
        markdown=True
    )
    agent.print_response('你能做什么', stream=True)


if __name__ == "__main__":
    main()
