import logging

class BasePrompt:
    name: str
    version: str
    prompt: str
    vars: list[str]

    def __init__(self, name: str, version: str, prompt: str, vars: list[str] = None):
        self.name = name
        self.version = version
        self.prompt = prompt
        self.vars = vars or []
        
    def get_prompt_id(self):
        return f'prompt_{self.name}_{self.version}'
        
    def get_prompt(self, vars: dict):
        """将变量字典填充到prompt模板中
        
        Args:
            vars: 变量字典，键为变量名，值为要替换的内容
            
        Returns:
            替换后的prompt字符串
            
        Raises:
            KeyError: 如果vars中缺少必需的变量
        """
        # 检查所有变量是否都有值
        missing_vars = [var for var in self.vars if var not in vars]
        if missing_vars:
            logging.warning(f"Prompt {self.name} is missing values for variables: {', '.join(missing_vars)}")
        
        return self.prompt.format(**vars)