# AI Agent提示词管理系统设计方案

## 原始设计方案（完整版）

### 1. 结构化存储格式 (YAML)
```yaml
version: 1.0.0
metadata:
  created_at: timestamp
  last_modified: timestamp 
prompt:
  id: unique_id
  name: prompt_name
  content: "实际提示词内容"
  parameters:
    temperature: 0.7
    max_tokens: 1000
history:
  - version: previous_version
    modified_at: timestamp
    change_description: "修改说明"
```

### 2. 完整版目录结构
```
prompts/
├── agent_prompts/    # 当前使用的提示词
├── templates/        # 提示词模板
└── versions/         # 历史版本存档
```

---

## 简化版设计方案（推荐）

### 1. 精简目录结构
```
prompts/
├── active/          # 当前使用的提示词(YAML格式)
│   ├── system/      # 系统级提示词
│   ├── agent/       # Agent特定提示词  
│   └── templates/   # 基础模板
├── .gitattributes   # Git配置
└── README.md        # 使用说明
```

### 2. Git版本控制方案
1. **分支策略**:
   - `main`: 稳定版本
   - `dev`: 开发分支
   - `feature/*`: 功能开发分支

2. **核心操作**:
```bash
# 创建新提示词
git checkout -b feat/add-new-prompt
git add active/agent/new_prompt.yaml
git commit -m "feat: add new prompt"

# 版本回滚
git checkout COMMIT_HASH -- active/agent/prompt.yaml
```

### 3. 实施步骤
1. 初始化Git仓库:
```bash
cd prompts && git init
```

2. 添加基础文件:
```bash
touch .gitattributes README.md
```

3. 创建目录结构:
```bash
mkdir -p active/{system,agent,templates}
```

## 方案选择建议
- **推荐使用简化版方案**：更适合中小规模项目
- 完整版方案可作为未来扩展参考