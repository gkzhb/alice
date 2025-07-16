import asyncio
from pydantic import BaseModel
from agno.storage.sqlite import SqliteStorage
from agno.utils.pprint import pprint_run_response
from alice.model.llm import ds_chat_model
from alice.agents.structure_fixer import StructureFixerAgent
from alice.agents.translater import TranslateScript


# 定义测试用的数据模型
class TestDataModel(BaseModel):
    name: str
    age: int
    email: str
    is_active: bool = True


# 初始化存储
storage = SqliteStorage(
    table_name="structure_fixer_result",
    db_file="data/dev/structure_fixer.db",
)

# 创建 StructureFixerAgent 实例
structure_fixer = StructureFixerAgent(model=ds_chat_model, data_model=TestDataModel)
# 创建新的StructureFixerAgent实例，使用TranslateScript作为数据模型
fix_translate_agent = StructureFixerAgent(
    model=ds_chat_model, data_model=TranslateScript
)


async def run_fix_structure(agent: StructureFixerAgent, raw_data: str):
    """
    运行结构修复逻辑
    """
    try:
        result = await agent.arun(raw_data)
        print("修复成功:")
        pprint_run_response(result)
        return result
    except ValueError as e:
        print(f"修复失败: {e}")
        return None


async def test_cases():
    """
    测试不同场景的输入
    """
    # 测试用例1: 完整正确的数据
    case1 = """{
        "name": "张三",
        "age": 30,
        "email": "zhangsan@example.com"
    }"""

    # 测试用例2: 缺少必填字段
    case2 = """{
        "name": "李四",
        "email": "lisi@example.com"
    }"""

    # 测试用例3: 类型错误
    case3 = """{
        "name": "王五",
        "age": "25",  # 字符串而不是数字
        "email": "wangwu@example.com"
    }"""

    # 测试用例4: 额外字段
    case4 = """{
        "name": "赵六",
        "age": 35,
        "email": "zhaoliu@example.com",
        "address": "北京"
    }"""

    # 测试用例5: 不完整的JSON
    case5 = """{
        "name": "钱七",
        "age": 40,
        "email": "qianqi@example.com"
    """  # 缺少闭合大括号

    # 测试用例6: 语法错误的JSON
    case6 = """{
        "name": "孙八",
        "age": 45,
        "email": "sunba@example.com",
        "is_active": "true"  # 应该是布尔值而不是字符串
    }"""

    # 测试用例7: 非JSON纯文本
    case7 = "这是一个纯文本字符串，不是JSON格式"

    print("测试用例1: 完整正确的数据")
    await run_fix_structure(structure_fixer, case1)

    print("\n测试用例2: 缺少必填字段")
    await run_fix_structure(structure_fixer, case2)

    print("\n测试用例3: 类型错误")
    await run_fix_structure(structure_fixer, case3)

    print("\n测试用例4: 额外字段")
    await run_fix_structure(structure_fixer, case4)

    print("\n测试用例5: 不完整的JSON")
    await run_fix_structure(structure_fixer, case5)

    print("\n测试用例6: 语法错误的JSON")
    await run_fix_structure(structure_fixer, case6)

    print("\n测试用例7: 非JSON纯文本")
    await run_fix_structure(structure_fixer, case7)

    # 添加测试用例8: TranslateScript模型的结构修复测试
    print("\n测试用例8: TranslateScript模型的结构修复")

    # 子测试8.1: 有效TranslateScript数据
    print("  子测试8.1: 有效的TranslateScript数据")
    valid_translate_data = """{
        "translated": "Hello, World!",
        "glossary": "World: 世界"
    }"""
    await run_fix_structure(fix_translate_agent, valid_translate_data)

    # 子测试8.2: 缺少必要字段的TranslateScript数据
    print("\n  子测试8.2: 缺少必要字段")
    missing_field_data = """{
        "translated": "Testing missing glossary"
    }"""
    await run_fix_structure(fix_translate_agent, missing_field_data)

    # 子测试8.3: 字段类型错误
    print("\n  子测试8.3: 字段类型错误")
    wrong_type_data = """{
        "translated": "Testing type error",
        "glossary": 123
    }"""
    await run_fix_structure(fix_translate_agent, wrong_type_data)

    # 子测试8.4: 非法 JSON
    print("\n  子测试8.4: 非法 JSON")
    wrong_type_data = """{
        "translated": "Testing type error",
        "glossary": "123"
    }```"""
    await run_fix_structure(fix_translate_agent, wrong_type_data)


async def main():
    await test_cases()


if __name__ == "__main__":
    asyncio.run(main())
