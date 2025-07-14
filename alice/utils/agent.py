def get_agent_id(name:str, version: str) -> str:
    """get agent unique name"""
    return f'agent_{name}_{version}'