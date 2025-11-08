# 🧠 DeepAgents 项目深度讲解

## 📋 目录
1. [项目概述](#项目概述)
2. [核心概念](#核心概念)
3. [架构设计](#架构设计)
4. [核心组件详解](#核心组件详解)
5. [CLI工具分析](#cli工具分析)
6. [技术实现细节](#技术实现细节)
7. [使用场景与最佳实践](#使用场景与最佳实践)

---

## 项目概述

### 项目定位
**DeepAgents** 是一个基于 LangGraph 构建的通用"深度智能体"框架，旨在解决传统 LLM Agent 在复杂、多步骤任务中的"浅层"问题。

### 核心问题
传统 Agent 架构（LLM + 工具循环调用）存在以下局限：
- ❌ **缺乏规划能力**：无法将复杂任务分解为可管理的步骤
- ❌ **上下文窗口限制**：长工具结果会快速填满上下文窗口
- ❌ **单一执行模式**：无法并行处理独立任务
- ❌ **缺乏持久化**：无法跨会话保存工作状态

### 解决方案
DeepAgents 通过四个核心能力解决这些问题：
1. **规划工具** (`write_todos`) - 任务分解与进度跟踪
2. **文件系统工具** (`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`) - 上下文外化存储
3. **子智能体** (`task` tool) - 上下文隔离与并行执行
4. **详细提示词** - 引导 Agent 正确使用工具

---

## 核心概念

### 1. Deep Agent vs Shallow Agent

**Shallow Agent（浅层智能体）**：
```
用户请求 → LLM → 工具调用 → LLM → 工具调用 → ... → 响应
```
- 线性执行，缺乏规划
- 上下文快速膨胀
- 难以处理多步骤复杂任务

**Deep Agent（深度智能体）**：
```
用户请求 → 规划（write_todos）→ 并行子任务 → 文件系统存储 → 结果合成 → 响应
```
- 先规划后执行
- 上下文外化到文件系统
- 支持并行子任务
- 支持长期记忆

### 2. 中间件架构（Middleware Architecture）

DeepAgents 采用**可组合的中间件模式**，每个核心功能都是独立的中间件：

```
Agent
├── TodoListMiddleware        # 规划工具
├── FilesystemMiddleware      # 文件系统工具
├── SubAgentMiddleware        # 子智能体工具
├── SummarizationMiddleware    # 上下文摘要
└── Custom Middleware          # 用户自定义中间件
```

**优势**：
- ✅ 模块化设计，易于扩展
- ✅ 可以独立使用任何中间件
- ✅ 支持自定义中间件组合

---

## 架构设计

### 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                    User Application                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              create_deep_agent()                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │         LangGraph Agent (create_agent)            │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │         Middleware Stack                    │ │  │
│  │  │  ┌───────────────────────────────────────┐ │ │  │
│  │  │  │ TodoListMiddleware                    │ │ │  │
│  │  │  │ - write_todos tool                    │ │ │  │
│  │  │  └───────────────────────────────────────┘ │ │  │
│  │  │  ┌───────────────────────────────────────┐ │ │  │
│  │  │  │ FilesystemMiddleware                   │ │ │  │
│  │  │  │ - ls, read_file, write_file, edit_file │ │ │  │
│  │  │  │ - glob, grep                          │ │ │  │
│  │  │  │ - Backend: StateBackend/StoreBackend   │ │ │  │
│  │  │  └───────────────────────────────────────┘ │ │  │
│  │  │  ┌───────────────────────────────────────┐ │ │  │
│  │  │  │ SubAgentMiddleware                     │ │ │  │
│  │  │  │ - task tool                            │ │ │  │
│  │  │  │ - General-purpose subagent             │ │ │  │
│  │  │  │ - Custom subagents                     │ │ │  │
│  │  │  └───────────────────────────────────────┘ │ │  │
│  │  │  ┌───────────────────────────────────────┐ │ │  │
│  │  │  │ SummarizationMiddleware                │ │ │  │
│  │  │  │ - Auto-summarize long contexts         │ │ │  │
│  │  │  └───────────────────────────────────────┘ │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 数据流

```
1. 用户输入
   ↓
2. Agent 接收消息
   ↓
3. Middleware 处理（添加工具、修改提示词）
   ↓
4. LLM 生成工具调用
   ↓
5. 工具执行（可能触发子智能体）
   ↓
6. 结果返回（可能写入文件系统）
   ↓
7. LLM 处理结果，继续或结束
```

---

## 核心组件详解

### 1. TodoListMiddleware - 规划工具

**功能**：为 Agent 提供 `write_todos` 工具，用于任务分解和进度跟踪。

**实现位置**：`langchain.agents.middleware.TodoListMiddleware`

**工作原理**：
- Agent 在开始复杂任务前调用 `write_todos` 创建待办列表
- 执行过程中可以更新待办项状态
- 支持动态调整计划

**示例**：
```python
# Agent 内部调用
write_todos([
    {"id": "1", "content": "研究 LangGraph", "status": "pending"},
    {"id": "2", "content": "编写报告", "status": "pending"}
])
```

### 2. FilesystemMiddleware - 文件系统工具

**功能**：提供6个文件系统工具，支持上下文外化存储。

**工具列表**：
- `ls(path)` - 列出目录文件
- `read_file(path, offset, limit)` - 读取文件（支持分页）
- `write_file(path, content)` - 创建新文件
- `edit_file(path, old_string, new_string, replace_all)` - 编辑文件
- `glob(pattern, path)` - 模式匹配查找文件
- `grep(pattern, path, glob, output_mode)` - 文本搜索

**后端架构**：

DeepAgents 使用**可插拔后端架构**，支持多种存储方式：

#### BackendProtocol 协议

所有后端必须实现 `BackendProtocol` 接口：

```python
class BackendProtocol(Protocol):
    def ls_info(self, path: str) -> list[FileInfo]
    def read(self, file_path: str, offset: int, limit: int) -> str
    def write(self, file_path: str, content: str) -> WriteResult
    def edit(self, file_path: str, old_string: str, new_string: str, replace_all: bool) -> EditResult
    def grep_raw(self, pattern: str, path: str | None, glob: str | None) -> list[GrepMatch] | str
    def glob_info(self, pattern: str, path: str) -> list[FileInfo]
```

#### 后端实现

**StateBackend**（默认）：
- 存储在 LangGraph 状态中
- 临时存储，会话结束后消失
- 适合短期任务

**FilesystemBackend**：
- 存储在真实文件系统
- 持久化存储，跨会话保留
- 适合长期项目

**StoreBackend**：
- 使用 LangGraph Store API
- 支持数据库、S3 等外部存储
- 适合分布式场景

**CompositeBackend**：
- 组合多个后端
- 基于路径前缀路由
- 示例：`/memories/` → StoreBackend，其他 → StateBackend

**关键特性**：

1. **大工具结果自动外化**：
   - 当工具返回结果超过 `tool_token_limit_before_evict`（默认20000 tokens）
   - 自动写入文件系统 `/large_tool_results/{tool_call_id}`
   - 返回摘要和文件路径，Agent 可以按需读取

2. **路径安全验证**：
   - 防止路径遍历攻击（`..`, `~`）
   - 支持路径前缀限制
   - 统一路径格式（以 `/` 开头）

3. **文件状态管理**：
   - 使用 LangGraph 的 `Annotated` reducer 管理文件状态
   - 支持文件删除（通过 `None` 值标记）

### 3. SubAgentMiddleware - 子智能体工具

**功能**：提供 `task` 工具，允许主 Agent 启动子智能体处理独立任务。

**核心优势**：
- ✅ **上下文隔离**：子智能体的上下文不会污染主 Agent
- ✅ **并行执行**：可以同时启动多个子智能体
- ✅ **专业化**：可以为不同领域创建专门的子智能体
- ✅ **令牌节省**：子智能体返回简洁结果，而非完整历史

**子智能体类型**：

1. **General-purpose Agent**（默认）：
   - 与主 Agent 相同的工具和能力
   - 用于上下文隔离的通用任务

2. **Custom SubAgents**：
   - 自定义提示词、工具、模型
   - 用于特定领域的专业化任务

**工作流程**：

```
主 Agent
  ↓
调用 task(description, subagent_type)
  ↓
创建子智能体实例（隔离状态）
  ↓
子智能体执行任务（可能多轮对话）
  ↓
返回最终结果（单条消息）
  ↓
主 Agent 接收结果并继续
```

**状态隔离机制**：

子智能体接收主 Agent 的状态副本，但排除：
- `messages` - 消息历史（子智能体有自己的）
- `todos` - 待办列表（子智能体有自己的）

子智能体可以更新其他状态键（如 `files`），这些更新会合并回主 Agent。

**使用场景**：

✅ **适合使用子智能体**：
- 复杂、多步骤的独立任务
- 需要深度研究的任务
- 可以并行执行的独立任务
- 需要隔离上下文的任务

❌ **不适合使用子智能体**：
- 简单任务（几个工具调用）
- 需要看到中间步骤的任务
- 需要与主 Agent 持续交互的任务

### 4. 其他中间件

**SummarizationMiddleware**：
- 自动摘要长上下文
- 当上下文超过 `max_tokens_before_summary`（默认170000）时触发
- 保留最近的 `messages_to_keep`（默认6）条消息

**AnthropicPromptCachingMiddleware**：
- 利用 Anthropic 的提示词缓存功能
- 减少重复提示词的令牌消耗

**PatchToolCallsMiddleware**：
- 修复工具调用的兼容性问题

---

## CLI工具分析

### 架构概览

DeepAgents CLI 是一个交互式命令行工具，提供完整的 Agent 交互体验。

**模块结构**：
```
deepagents_cli/
├── __main__.py      # 入口点
├── main.py          # CLI 主循环
├── config.py        # 配置和常量
├── tools.py         # 自定义工具（HTTP、Web搜索）
├── ui.py            # UI 渲染
├── input.py         # 输入处理
├── commands.py      # 命令处理
├── execution.py     # 任务执行
└── agent.py         # Agent 创建和管理
```

### 核心功能

#### 1. 文件上下文注入
- 输入 `@filename` 自动补全并注入文件内容
- 支持 Tab 补全

#### 2. 交互式命令
- `/help` - 显示帮助
- `/clear` - 清屏并重置对话
- `/tokens` - 显示令牌使用情况
- `/quit` 或 `/exit` - 退出

#### 3. Bash 命令执行
- 输入 `!command` 执行 bash 命令
- 支持 Human-in-the-Loop 审批

#### 4. Todo 列表可视化
- 实时显示 Agent 创建的待办列表
- 支持复选框状态更新

#### 5. 文件操作摘要和 Diff 查看器
- 文件读取显示摘要（行数、范围）
- 写入/编辑显示 diff（使用 Rich 库）
- 支持语法高亮

#### 6. Human-in-the-Loop (HITL)
- Shell 命令需要用户审批
- 交互式箭头键菜单
- 文件编辑显示 diff 供审查

### Agent 存储

每个 Agent 的状态存储在 `~/.deepagents/AGENT_NAME/`：
- `agent.md` - Agent 的自定义指令（长期记忆）
- `memories/` - 额外的上下文文件
- `history` - 命令历史

### Agent 创建流程

```python
# 1. 创建复合后端
backend = CompositeBackend(
    default=FilesystemBackend(working_dir),
    routes={"/memories/": StoreBackend(store)}
)

# 2. 创建 Agent
agent = create_deep_agent(
    model=model,
    tools=[http_request, web_search],
    system_prompt=system_prompt,
    backend=backend,
    checkpointer=checkpointer,
    interrupt_on={"shell": {...}}  # HITL 配置
)
```

---

## 技术实现细节

### 1. 状态管理

DeepAgents 使用 LangGraph 的状态管理机制：

**FilesystemState**：
```python
class FilesystemState(AgentState):
    files: Annotated[
        NotRequired[dict[str, FileData]], 
        _file_data_reducer
    ]
```

**文件数据格式**：
```python
class FileData(TypedDict):
    content: list[str]      # 文件行列表
    created_at: str         # ISO 8601 时间戳
    modified_at: str        # ISO 8601 时间戳
```

**Reducer 机制**：
- `_file_data_reducer` 处理文件状态更新
- 支持文件删除（通过 `None` 值）
- 自动合并更新

### 2. 工具调用拦截

**大结果外化**：
```python
def wrap_tool_call(self, request, handler):
    tool_result = handler(request)
    if tool_result 太大:
        # 写入文件系统
        file_path = f"/large_tool_results/{tool_call_id}"
        backend.write(file_path, content)
        # 返回摘要消息
        return ToolMessage("结果已保存到 {file_path}...")
    return tool_result
```

### 3. 子智能体调用

**状态准备**：
```python
def _validate_and_prepare_state(subagent_type, description, runtime):
    # 排除 messages 和 todos
    subagent_state = {
        k: v for k, v in runtime.state.items() 
        if k not in _EXCLUDED_STATE_KEYS
    }
    # 添加新消息
    subagent_state["messages"] = [HumanMessage(content=description)]
    return subagent, subagent_state
```

**结果合并**：
```python
def _return_command_with_state_update(result, tool_call_id):
    # 提取状态更新（排除 messages）
    state_update = {
        k: v for k, v in result.items() 
        if k not in _EXCLUDED_STATE_KEYS
    }
    # 返回 Command 对象
    return Command(update={
        **state_update,
        "messages": [ToolMessage(result["messages"][-1].text, ...)]
    })
```

### 4. 路径安全

**路径验证**：
```python
def _validate_path(path, allowed_prefixes=None):
    # 防止路径遍历
    if ".." in path or path.startswith("~"):
        raise ValueError("Path traversal not allowed")
    
    # 规范化路径
    normalized = os.path.normpath(path).replace("\\", "/")
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    
    # 检查前缀限制
    if allowed_prefixes and not any(...):
        raise ValueError("Path must start with allowed prefix")
    
    return normalized
```

---

## 使用场景与最佳实践

### 1. 研究助手

**场景**：深度研究某个主题并生成报告

**关于 Tavily**：
Tavily 是一个专为 AI Agent 设计的网络搜索 API 服务，提供：
- 🚀 **快速响应**：优化的搜索速度，适合实时 Agent 交互
- 🎯 **AI 优化**：搜索结果针对 LLM 处理进行了优化，减少幻觉
- 🔒 **生产就绪**：高可用性和高速率限制，适合企业级应用
- 📊 **结构化结果**：返回格式化的搜索结果，包含标题、URL、摘要等

**定价信息**：
- Tavily 提供免费套餐和付费套餐
- 免费套餐通常包含有限的 API 调用次数，适合开发测试
- 付费套餐提供更高的调用限制和更多功能
- 获取 API Key：访问 [https://tavily.com](https://tavily.com) 注册账号

**在 DeepAgents CLI 中的实现**：
- Web 搜索功能**不是**写死的，而是可选的
- 如果设置了 `TAVILY_API_KEY` 环境变量，`web_search` 工具会自动可用
- 如果没有设置 API Key：
  - `web_search` 工具仍然存在，但调用时会返回错误提示
  - CLI 启动时会显示警告信息，提示 Web 搜索已禁用
  - 用户可以选择不设置 API Key，只使用其他工具
- 支持 Human-in-the-Loop (HITL) 审批，每次搜索前会提示用户确认（因为会消耗 API credits）

在 DeepAgents 中，Tavily 常用于：
- Web 搜索工具（`web_search`）
- 研究助手子智能体
- 实时信息获取

**实现**：
```python
from tavily import TavilyClient

# 初始化 Tavily 客户端
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# 定义搜索工具
def internet_search(query: str, max_results: int = 5):
    """运行网络搜索"""
    return tavily_client.search(query, max_results=max_results)

# 创建研究助手 Agent
agent = create_deep_agent(
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=[
        {
            "name": "research-agent",
            "description": "深度研究单个主题",
            "system_prompt": "你是专业研究员...",
            "tools": [internet_search]
        }
    ]
)
```

**工作流程**：
1. Agent 创建研究计划（write_todos）
2. 并行启动多个 research-agent 研究不同子主题
3. 将研究结果写入文件系统
4. 合成最终报告

### 2. 代码助手

**场景**：分析代码库、重构、添加功能

**实现**：
```python
agent = create_deep_agent(
    tools=[...],
    backend=CompositeBackend(
        default=FilesystemBackend(working_dir),
        routes={"/memories/": StoreBackend(store)}
    ),
    interrupt_on={
        "shell": {"allowed_decisions": ["approve", "edit", "reject"]}
    }
)
```

**最佳实践**：
- ✅ 使用文件系统存储代码上下文
- ✅ 使用 `/memories/` 存储项目知识
- ✅ 启用 HITL 审批危险操作
- ✅ 使用子智能体隔离复杂重构任务

### 3. 数据分析

**场景**：分析大型数据集并生成报告

**实现**：
```python
agent = create_deep_agent(
    tools=[data_analysis_tool, visualization_tool],
    subagents=[
        {
            "name": "data-analyst",
            "description": "专业数据分析",
            "tools": [data_analysis_tool]
        }
    ]
)
```

**工作流程**：
1. 将数据文件写入文件系统
2. 使用子智能体分析不同数据维度
3. 合成分析结果
4. 生成可视化报告

### 最佳实践总结

#### ✅ DO（推荐做法）

1. **使用规划工具**：
   - 复杂任务前先创建待办列表
   - 动态更新计划

2. **利用文件系统**：
   - 将长工具结果写入文件
   - 使用分页读取大文件
   - 使用 `/memories/` 存储长期知识

3. **合理使用子智能体**：
   - 独立任务使用子智能体
   - 并行执行独立任务
   - 为不同领域创建专门子智能体

4. **自定义提示词**：
   - 为特定用例编写详细提示词
   - 明确工具使用规则

#### ❌ DON'T（避免做法）

1. **不要过度使用子智能体**：
   - 简单任务直接执行
   - 需要看到中间步骤的任务不使用子智能体

2. **不要忽略上下文管理**：
   - 大文件要分页读取
   - 及时清理不需要的文件

3. **不要硬编码路径**：
   - 使用绝对路径
   - 利用 glob 和 grep 查找文件

---

## 总结

DeepAgents 通过以下创新解决了传统 Agent 的局限性：

1. **规划能力**：通过 TodoListMiddleware 实现任务分解
2. **上下文管理**：通过 FilesystemMiddleware 实现上下文外化
3. **并行执行**：通过 SubAgentMiddleware 实现任务隔离和并行
4. **模块化设计**：通过中间件架构实现灵活扩展

这使得 DeepAgents 能够处理传统 Agent 无法处理的复杂、长期任务，是构建生产级 AI Agent 应用的强大框架。

---

## LLM 模型支持

### 支持的模型类型

DeepAgents 基于 LangChain，因此**支持所有 LangChain 支持的 LLM 模型**。这包括但不限于：

#### 1. Anthropic Claude 系列（默认）
- ✅ `claude-sonnet-4-5-20250929`（默认）
- ✅ `claude-sonnet-4-20250514`
- ✅ `claude-opus-4`
- ✅ `claude-haiku-4`
- ✅ 其他 Claude 模型

#### 2. OpenAI 系列
- ✅ `gpt-5-mini`（CLI 默认）
- ✅ `gpt-5`
- ✅ `gpt-4o`
- ✅ `gpt-4.1`
- ✅ `gpt-4-turbo`
- ✅ `gpt-3.5-turbo`
- ✅ 其他 OpenAI 模型

#### 3. 其他 LangChain 支持的模型
- ✅ Google Gemini 系列
- ✅ Mistral AI 系列
- ✅ Cohere 系列
- ✅ 其他 LangChain 集成的模型

### 配置方式

#### 方式 1：使用 `init_chat_model`（推荐）

```python
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

# 使用字符串格式（LangChain 标准格式）
model = init_chat_model("openai:gpt-4o")
# 或
model = init_chat_model("anthropic:claude-sonnet-4-20250514")

agent = create_deep_agent(model=model)
```

#### 方式 2：直接传入模型实例

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from deepagents import create_deep_agent

# OpenAI
model = ChatOpenAI(model="gpt-4o", temperature=0.7)
agent = create_deep_agent(model=model)

# Anthropic
model = ChatAnthropic(model_name="claude-sonnet-4-5-20250929", max_tokens=20000)
agent = create_deep_agent(model=model)
```

#### 方式 3：使用字符串（自动解析）

```python
from deepagents import create_deep_agent

# 直接传入字符串，DeepAgents 会使用默认模型
agent = create_deep_agent(model="anthropic:claude-sonnet-4-20250514")
```

### CLI 中的模型配置

在 DeepAgents CLI 中，模型选择基于环境变量：

**OpenAI 模型**：
```bash
export OPENAI_API_KEY=your_api_key_here
export OPENAI_MODEL=gpt-5-mini  # 可选，默认为 gpt-5-mini
```

**Anthropic 模型**：
```bash
export ANTHROPIC_API_KEY=your_api_key_here
export ANTHROPIC_MODEL=claude-sonnet-4-5-20250929  # 可选，默认为 claude-sonnet-4-5-20250929
```

**优先级**：
1. 如果设置了 `OPENAI_API_KEY`，使用 OpenAI 模型
2. 否则如果设置了 `ANTHROPIC_API_KEY`，使用 Anthropic 模型
3. 如果都没有设置，CLI 会报错退出

### 子智能体的模型配置

每个子智能体可以独立配置模型：

```python
subagents = [
    {
        "name": "research-agent",
        "description": "深度研究助手",
        "system_prompt": "你是专业研究员...",
        "tools": [internet_search],
        "model": "openai:gpt-4o",  # 子智能体使用不同的模型
    },
    {
        "name": "code-reviewer",
        "description": "代码审查助手",
        "system_prompt": "你是代码审查专家...",
        "model": "anthropic:claude-sonnet-4-20250514",  # 另一个模型
    }
]

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-5-20250929",  # 主 Agent 模型
    subagents=subagents
)
```

### 模型选择建议

| 使用场景 | 推荐模型 | 原因 |
|---------|---------|------|
| 代码生成和编辑 | Claude Sonnet 4 | 代码理解能力强，上下文窗口大 |
| 快速响应任务 | GPT-5-mini / Claude Haiku | 速度快，成本低 |
| 复杂推理任务 | Claude Opus 4 / GPT-5 | 推理能力强 |
| 研究分析 | Claude Sonnet 4 | 长上下文，分析能力强 |
| 成本敏感场景 | GPT-5-mini / Claude Haiku | 性价比高 |

### 接入其他模型供应商

DeepAgents 基于 LangChain，支持接入任何兼容 OpenAI API 格式的模型供应商。以下是几种常见方式：

#### 方式 1：使用 OpenAI 兼容 API（推荐）

如果模型供应商提供 OpenAI 兼容的 API（如硅基流动、OpenRouter、Together AI 等），可以直接使用 `ChatOpenAI` 并指定 `base_url`：

```python
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent

# 硅基流动示例
model = ChatOpenAI(
    model="deepseek-chat",  # 或其他模型名称
    base_url="https://api.siliconflow.cn/v1",  # 硅基流动 API 地址
    api_key="your_siliconflow_api_key",
    temperature=0.7,
)

agent = create_deep_agent(model=model)
```

#### 方式 2：使用环境变量配置

```bash
# 设置自定义 API 地址和密钥
export OPENAI_API_BASE=https://api.siliconflow.cn/v1
export OPENAI_API_KEY=your_siliconflow_api_key
export OPENAI_MODEL=deepseek-chat
```

然后在代码中：
```python
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent

# 会自动读取环境变量
model = ChatOpenAI()
agent = create_deep_agent(model=model)
```

#### 方式 3：使用 LangChain 的 `init_chat_model`

如果供应商在 LangChain 中有专门的集成：

```python
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

# 使用 LangChain 支持的格式
model = init_chat_model("siliconflow:deepseek-chat")  # 如果 LangChain 支持
# 或
model = init_chat_model("openai:gpt-4o", base_url="https://api.siliconflow.cn/v1")

agent = create_deep_agent(model=model)
```

#### 方式 4：自定义模型类

如果供应商有特殊的 API 格式，可以创建自定义的 LangChain 模型类：

```python
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from deepagents import create_deep_agent

class CustomModelProvider(BaseChatModel):
    """自定义模型提供商"""
    
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        # 实现自定义 API 调用逻辑
        # 返回 ChatResult
        pass
    
    @property
    def _llm_type(self) -> str:
        return "custom_provider"

# 使用自定义模型
model = CustomModelProvider()
agent = create_deep_agent(model=model)
```

#### 常见模型供应商接入示例

**硅基流动（SiliconFlow）**：
```python
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent

model = ChatOpenAI(
    model="deepseek-chat",  # 或其他可用模型
    base_url="https://api.siliconflow.cn/v1",
    api_key=os.environ.get("SILICONFLOW_API_KEY"),
)

agent = create_deep_agent(model=model)
```

**OpenRouter**：
```python
model = ChatOpenAI(
    model="openai/gpt-4o",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    default_headers={"HTTP-Referer": "your-app-url"},  # 可选
)
```

**Together AI**：
```python
model = ChatOpenAI(
    model="meta-llama/Llama-3-70b-chat-hf",
    base_url="https://api.together.xyz/v1",
    api_key=os.environ.get("TOGETHER_API_KEY"),
)
```

**本地模型（如 Ollama）**：
```python
from langchain_ollama import ChatOllama
from deepagents import create_deep_agent

model = ChatOllama(
    model="llama3",
    base_url="http://localhost:11434",  # Ollama 默认地址
)

agent = create_deep_agent(model=model)
```

#### CLI 中接入自定义模型供应商

修改 `libs/deepagents-cli/deepagents_cli/config.py` 中的 `create_model()` 函数：

```python
def create_model():
    """Create the appropriate model based on available API keys."""
    # 优先检查自定义供应商
    siliconflow_key = os.environ.get("SILICONFLOW_API_KEY")
    if siliconflow_key:
        from langchain_openai import ChatOpenAI
        model_name = os.environ.get("SILICONFLOW_MODEL", "deepseek-chat")
        console.print(f"[dim]Using SiliconFlow model: {model_name}[/dim]")
        return ChatOpenAI(
            model=model_name,
            base_url="https://api.siliconflow.cn/v1",
            api_key=siliconflow_key,
            temperature=0.7,
        )
    
    # 原有的 OpenAI 和 Anthropic 检查...
    openai_key = os.environ.get("OPENAI_API_KEY")
    # ...
```

#### 注意事项

1. **API 兼容性**：确保模型供应商的 API 兼容 OpenAI 格式（包括消息格式、工具调用格式等）
2. **工具调用支持**：某些模型可能不支持工具调用（function calling），需要确认
3. **上下文窗口**：不同供应商的模型上下文窗口大小不同
4. **速率限制**：注意不同供应商的 API 速率限制
5. **错误处理**：自定义供应商可能需要额外的错误处理逻辑

### 注意事项

1. **API Key 配置**：使用任何模型都需要配置相应的 API Key
2. **上下文窗口**：不同模型的上下文窗口大小不同，注意文件系统工具的分页读取
3. **工具调用能力**：确保选择的模型支持工具调用（function calling）
4. **成本考虑**：不同模型的定价差异很大，根据需求选择合适的模型
5. **API 兼容性**：使用第三方供应商时，确保 API 格式兼容

---

## 参考资料

- [官方文档](https://docs.langchain.com/oss/python/deepagents/overview)
- [GitHub 仓库](https://github.com/langchain-ai/deepagents)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [LangChain 模型集成](https://python.langchain.com/docs/integrations/chat/)

