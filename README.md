# 🧠🤖 Deep Agents - HKEX 港股智能分析系统

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

基于 Deep Agents 框架开发的港股交易数据分析智能代理系统，专门用于处理港交所公告、PDF 文档解析和智能摘要生成。

## ✨ 核心特性

- 📄 **智能 PDF 解析**：自动识别港交所公告格式，支持大型年报（自动截断 > 50k 字符）
- 🔍 **内容摘要生成**：自动生成关键信息摘要和市场影响分析
- 📊 **结构化数据提取**：从非结构化文档中提取财务数据、交易信息
- 💾 **智能缓存管理**：PDF 文档和提取内容的持久化存储
- ⚡ **LLM Token 优化**：大型 PDF 自动保存到缓存，防止 token 溢出
- 🌈 **优雅用户界面**：ASCII 艺术字横幅（571 种字体）+ 彩虹渐变效果

<img src="deep_agents.png" alt="deep agent" width="600"/>

**技术致谢：本项目主要灵感来源于 Claude Code，旨在探索其通用化能力并进行专门化定制。**

---

## 🚀 快速开始

### 安装

```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install -r requirements.txt

# 或使用 poetry
poetry install
```

### 环境配置

创建 `.env` 文件并配置必要的环境变量：

```bash
# ========== LLM Provider API Keys ==========
# 优先级: SiliconFlow > OpenAI > Anthropic

# SiliconFlow (推荐 - 成本优化)
SILICONFLOW_API_KEY=your_siliconflow_api_key
SILICONFLOW_MODEL=deepseek-ai/DeepSeek-V3.1-Terminus  # 主Agent模型
SILICONFLOW_PDF_MODEL=Qwen/Qwen2.5-7B-Instruct       # PDF分析子Agent
SILICONFLOW_REPORT_MODEL=Qwen/Qwen2.5-72B-Instruct   # 报告生成子Agent

# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o  # 可选，默认gpt-5-mini

# Anthropic (Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929  # 可选

# ========== 模型参数 ==========
SILICONFLOW_TEMPERATURE=0.7           # 温度 (0.0-1.0)
SILICONFLOW_MAX_TOKENS=20000          # 最大token数
SILICONFLOW_TOP_P=0.9                 # Top-p采样 (可选)
SILICONFLOW_FREQUENCY_PENALTY=0.0     # 频率惩罚 (可选)
SILICONFLOW_PRESENCE_PENALTY=0.0      # 存在惩罚 (可选)
SILICONFLOW_API_TIMEOUT=60            # API超时(秒)
SILICONFLOW_API_RETRY=3               # 重试次数

# 子Agent独立温度配置 (可选)
SILICONFLOW_PDF_TEMPERATURE=0.5       # PDF分析温度
SILICONFLOW_REPORT_TEMPERATURE=0.7    # 报告生成温度

# ========== UI配置 ==========
HKEX_ASCII_FONT=slant                 # ASCII横幅字体 (571种可选)
HKEX_RAINBOW=true                     # 彩虹渐变效果 (true/false)

# ========== 其他功能 ==========
TAVILY_API_KEY=your_tavily_api_key    # 网络搜索功能
```

详细配置说明请参考 `.env.example` 文件。

### 使用示例

#### 命令行工具

```bash
# 启动 HKEX 交互式命令行
hkex

# 示例查询
> 00700 最新中期报告的摘要，并生成摘要md
> 03800 2024年报的关键财务数据
> 00875 最近的配售公告详情
```

**📖 完整使用指南**：[HKEX Agent 使用文档](docs/HKEX_AGENT_USAGE.md)
- 基础功能与高级用法
- 常见场景与故障排查
- 性能优化与最佳实践
- 4 个详细示例输出

#### Python API

```python
import os
from hkex_agent import HKEXAnalyzer

# 初始化分析器
analyzer = HKEXAnalyzer()

# 分析 PDF 公告
result = analyzer.analyze_announcement("path/to/hkex_announcement.pdf")

print("摘要:", result.summary)
print("关键数据:", result.key_data)
print("市场影响:", result.market_impact)
```

---

## 📋 项目架构

### 核心组件

**🧠 Deep Agents 框架**
- **规划工具**：内置 `write_todos` 工具，任务分解与进度跟踪
- **文件系统**：`ls`、`read_file`、`write_file`、`edit_file`、`glob`、`grep`
- **子代理生成**：内置 `task` 工具，上下文隔离与专门化处理
- **长期记忆**：基于 LangGraph Store 的跨线程持久化

**🏢 HKEX 专用功能**
- **PDF 解析引擎**：智能识别港交所公告格式，支持繁体中文
- **智能摘要生成**：自动识别公告类型和重要性，生成结构化摘要
- **数据提取**：财务指标、公司行动、市场事件自动提取
- **缓存优化**：PDF 文档和摘要结果的持久化存储

### 项目结构

```
deepagents-hk/
├── libs/
│   ├── deepagents/          # DeepAgents框架核心
│   │   ├── graph.py         # Agent图构建
│   │   ├── backends/        # 存储后端
│   │   ├── middleware/      # 中间件
│   │   └── tests/           # 框架测试
│   └── deepagents-cli/      # DeepAgents CLI工具
├── src/                     # HKEX应用代码 (作为src包)
│   ├── agents/              # 代理核心逻辑
│   │   ├── main_agent.py    # 主代理
│   │   └── subagents.py     # 子代理定义
│   ├── api/                 # API 接口
│   │   └── client.py        # 客户端
│   ├── cli/                 # 命令行工具 (src.cli包)
│   │   ├── config.py        # 配置和模型创建
│   │   ├── main.py          # 主入口
│   │   └── ...
│   ├── config/              # 配置模块
│   │   └── agent_config.py  # Agent模型配置
│   ├── services/            # 业务服务
│   │   ├── hkex_api.py      # 港交所 API
│   │   └── pdf_parser.py    # PDF 解析服务
│   ├── tools/               # 工具集合
│   │   ├── hkex_tools.py    # 港股专用工具
│   │   ├── pdf_tools.py     # PDF 处理工具
│   │   └── summary_tools.py # 摘要工具
│   └── prompts/             # 提示词模板
│       ├── main_system_prompt.md
│       └── pdf_analyzer_prompt.md
├── pdf_cache/               # PDF 缓存目录 (已 gitignore)
│   └── {stock_code}/        # 按股票代码分类
│       ├── {date}-{title}.pdf      # PDF 文件
│       ├── {date}-{title}.txt      # 文本缓存 (大型 PDF)
│       └── {date}-{title}_tables.json  # 表格缓存 (大型 PDF)
├── md/                      # 摘要存储目录 (已 gitignore)
├── docs/                    # 项目文档
├── .env                     # 环境变量配置
├── pyproject.toml           # 统一项目配置
└── README.md                # 项目说明
```

**重要说明**：
- 项目已统一到单一 `pyproject.toml` 配置
- `src` 目录作为完整的Python包，所有模块使用 `from src.xxx` 导入
- `hkex` 命令entry point: `src.cli.main:cli_main`
- 支持通过环境变量配置不同LLM模型和参数

---

## 📄 PDF 智能截断功能

### 功能概述

为了防止大型 PDF（如年报）导致 LLM token 溢出（如 03800 年报 206k 字符），系统实现了智能截断机制：

- ✅ **自动检测**：文本 > 50k 字符或表格 > 200 行时自动触发
- ✅ **完整保留**：全部内容保存到缓存文件（`.txt` 和 `_tables.json`）
- ✅ **预览返回**：工具返回前 5k 字符文本预览 + 前 5 个表格
- ✅ **清晰指引**：预览中包含完整路径和 `read_file()` 使用说明
- ✅ **向后兼容**：小型 PDF（< 50k）行为完全不变

### 工作原理

```python
# 1. 提取 PDF 内容（自动截断）
pdf_content = extract_pdf_content("path/to/large_annual_report.pdf")

# 2. 检查是否被截断
if pdf_content["truncated"]:
    print(f"预览文本: {pdf_content['text'][:100]}...")
    print(f"完整文本路径: {pdf_content['text_path']}")
    print(f"完整表格路径: {pdf_content['tables_path']}")
    
    # 3. 按需读取完整内容
    full_text = read_file(pdf_content["text_path"])
    full_tables = json.loads(read_file(pdf_content["tables_path"]))
else:
    # 小文档：直接使用全文
    full_text = pdf_content["text"]
    full_tables = pdf_content["tables"]
```

### 阈值配置

默认阈值（可在 `src/tools/pdf_tools.py` 中调整）：

```python
MAX_INLINE_TEXT_CHARS = 50_000  # 50k 字符 ≈ 12.5k tokens
MAX_INLINE_TABLE_ROWS = 200     # 表格总行数限制
TEXT_PREVIEW_CHARS = 5_000      # 预览长度
TABLE_PREVIEW_COUNT = 5         # 预览表格数量
```

### 缓存文件结构

```
pdf_cache/
└── 03800/
    ├── 2025-04-29-2024年报.pdf           # 原始 PDF
    ├── 2025-04-29-2024年报.txt           # 文本缓存（大型 PDF）
    └── 2025-04-29-2024年报_tables.json   # 表格缓存（JSON 格式）
```

### 性能优化

- **延迟写入**：仅截断时才写缓存，小文档零开销
- **原子写入**：临时文件 + 重命名，防止并发读取不完整数据
- **自动清理**：`cleanup_old_pdfs()` 同时清理 PDF 和缓存文件
- **警告抑制**：自动过滤 pdfminer 颜色空间警告，保持控制台输出清洁

### 测试验证

```bash
# 运行 PDF 截断功能测试
pytest libs/deepagents/tests/unit_tests/test_pdf_truncation.py -v
pytest libs/deepagents/tests/integration_tests/test_pdf_truncation_workflow.py -v
```

---

## 🛠️ 开发指南

### 环境设置

```bash
# 克隆项目
git clone <repository-url>
cd deepagents-hk

# 安装依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_pdf_parser.py

# 生成覆盖率报告
pytest --cov=src tests/
```

### 代码规范

本项目使用以下工具确保代码质量：

- **Ruff**: 代码检查和格式化
- **MyPy**: 类型检查
- **Black**: 代码格式化

```bash
# 运行代码检查
ruff check src/
mypy src/

# 格式化代码
ruff format src/
black src/
```

---

## 🔧 自定义 Deep Agents

### 模型配置

```python
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

model = init_chat_model("openai:gpt-4o")
agent = create_deep_agent(
    model=model,
)
```

### 系统提示词

```python
from deepagents import create_deep_agent

research_instructions = """You are an expert researcher. Your job is to conduct thorough research, and then write a polished report.
"""

agent = create_deep_agent(
    system_prompt=research_instructions,
)
```

### 工具集成

```python
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

agent = create_deep_agent(
    tools=[internet_search]
)
```

### 子代理配置

```python
research_subagent = {
    "name": "research-agent",
    "description": "Used to research more in depth questions",
    "system_prompt": "You are a great researcher",
    "tools": [internet_search],
    "model": "openai:gpt-4o",  # Optional override
}

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    subagents=[research_subagent]
)
```

### 中间件扩展

```python
from langchain_core.tools import tool
from deepagents import create_deep_agent
from langchain.agents.middleware import AgentMiddleware

@tool
def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."

class WeatherMiddleware(AgentMiddleware):
  tools = [get_weather]

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    middleware=[WeatherMiddleware()]
)
```

### 人机协同 (HITL)

```python
from langchain_core.tools import tool
from deepagents import create_deep_agent

@tool
def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[get_weather],
    interrupt_on={
        "get_weather": {
            "allowed_decisions": ["approve", "edit", "reject"]
        },
    }
)
```

---

## 📚 Deep Agents 中间件

Deep Agents 采用模块化中间件架构，自动附加以下中间件：

### TodoListMiddleware

规划工具，使代理能够将复杂任务分解为离散步骤，跟踪进度，并根据新信息调整计划。

```python
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_agent(
    model="anthropic:claude-sonnet-4-20250514",
    middleware=[
        TodoListMiddleware(
            system_prompt="Use the write_todos tool to..."
        ),
    ],
)
```

### FilesystemMiddleware

上下文管理工具，提供 `ls`、`read_file`、`write_file`、`edit_file` 等文件系统操作。

```python
from langchain.agents import create_agent
from deepagents.middleware.filesystem import FilesystemMiddleware

agent = create_agent(
    model="anthropic:claude-sonnet-4-20250514",
    middleware=[
        FilesystemMiddleware(
            backend=...,  # Optional: customize storage backend
            system_prompt="Write to the filesystem when...",
            custom_tool_descriptions={
                "ls": "Use the ls tool when...",
                "read_file": "Use the read_file tool to..."
            }
        ),
    ],
)
```

### SubAgentMiddleware

子代理生成工具，允许主代理生成专门的子代理进行上下文隔离。

```python
from langchain_core.tools import tool
from langchain.agents import create_agent
from deepagents.middleware.subagents import SubAgentMiddleware

@tool
def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."

agent = create_agent(
    model="claude-sonnet-4-20250514",
    middleware=[
        SubAgentMiddleware(
            default_model="claude-sonnet-4-20250514",
            default_tools=[],
            subagents=[
                {
                    "name": "weather",
                    "description": "This subagent can get weather in cities.",
                    "system_prompt": "Use the get_weather tool to get the weather in a city.",
                    "tools": [get_weather],
                    "model": "gpt-4.1",
                    "middleware": [],
                }
            ],
        )
    ],
)
```

---

## 🔌 MCP 集成

`deepagents` 库可以与 MCP 工具集成，使用 [Langchain MCP Adapter library](https://github.com/langchain-ai/langchain-mcp-adapters)。

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent

async def main():
    # Collect MCP tools
    mcp_client = MultiServerMCPClient(...)
    mcp_tools = await mcp_client.get_tools()

    # Create agent
    agent = create_deep_agent(tools=mcp_tools, ....)

    # Stream the agent
    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": "what is langgraph?"}]},
        stream_mode="values"
    ):
        if "messages" in chunk:
            chunk["messages"][-1].pretty_print()

asyncio.run(main())
```

---

## 📝 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- **Claude Code**: 本项目的主要灵感来源
- **LangGraph**: 强大的代理框架
- **Deep Agents**: 核心框架实现

---

## 📮 联系方式

如有问题或建议，请通过以下方式联系：

- **Issues**: [GitHub Issues](https://github.com/HK-CCASS/deepagents-hk/issues)
- **Email**: your-email@example.com

---

**🎉 开始使用 Deep Agents HKEX，体验智能化的港股分析！**
