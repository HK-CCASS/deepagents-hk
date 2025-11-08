# HKEX公告分析助手实现计划

## 项目结构

创建新的包 `src/hkex-agent/`，包含以下模块：

```
src/hkex-agent/
├── hkex_agent/
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── hkex_api.py          # 港交所API封装
│   │   └── pdf_parser.py        # PDF解析服务（含缓存）
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── hkex_tools.py        # DeepAgents工具（搜索、获取公告等）
│   │   └── pdf_tools.py         # PDF处理工具（智能缓存）
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── main_agent.py        # 主Agent创建
│   │   └── subagents.py         # 子Agent定义（PDF分析等）
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── __main__.py          # CLI入口（参考libs/deepagents-cli）
│   │   ├── main.py              # CLI主循环（参考libs/deepagents-cli/deepagents_cli/main.py）
│   │   ├── config.py            # 配置管理（参考libs/deepagents-cli/deepagents_cli/config.py）
│   │   ├── agent.py             # Agent创建（参考libs/deepagents-cli/deepagents_cli/agent.py）
│   │   ├── tools.py             # 工具定义（参考libs/deepagents-cli/deepagents_cli/tools.py）
│   │   ├── ui.py                # UI渲染（参考libs/deepagents-cli/deepagents_cli/ui.py）
│   │   ├── input.py             # 输入处理（参考libs/deepagents-cli/deepagents_cli/input.py）
│   │   ├── commands.py          # 命令处理（参考libs/deepagents-cli/deepagents_cli/commands.py）
│   │   ├── execution.py          # 任务执行（参考libs/deepagents-cli/deepagents_cli/execution.py）
│   │   └── token_utils.py       # Token统计（参考libs/deepagents-cli/deepagents_cli/token_utils.py）
│   └── api/
│       ├── __init__.py
│       └── client.py            # Python API客户端
├── pyproject.toml
└── README.md
```

## PDF缓存策略设计

### 存储结构

```
~/.hkex-agent/{AGENT_NAME}/
├── agent.md                    # Agent自定义指令
├── memories/                  # 长期记忆
└── pdf_cache/                 # PDF缓存（持久化）
    ├── 00673/                 # 按股票代码组织
    │   ├── 2025-10-08-翌日披露報表.pdf
    │   ├── 2025-09-30-中期業績公告.pdf
    │   └── ...
    ├── 00700/
    │   ├── 2025-10-15-季度報告.pdf
    │   └── ...
    └── ...
```

### 缓存机制

1. **文件命名**：`{公告日期}-{公告标题}.pdf`

   - 日期格式：`YYYY-MM-DD`（从API响应的DATE_TIME解析）
   - 标题清理：移除特殊字符（`/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`）
   - 文件名长度限制：避免过长（如超过200字符则截断并添加省略号）

2. **目录结构**：`/pdf_cache/{stock_code}/{日期-标题}.pdf`

   - 按股票代码组织，便于查找和管理

3. **缓存检查**：下载前先检查缓存路径，存在则直接返回路径
4. **跨会话持久化**：使用FilesystemBackend，确保缓存跨会话保留
5. **文件名清理**：提供 `sanitize_filename()` 函数处理特殊字符

## 实现步骤

### 1. 创建项目结构和依赖配置

- 创建 `src/hkex-agent/` 目录结构
- 创建 `pyproject.toml`，添加依赖：
  - `deepagents` (workspace依赖，路径：`../deepagents`)
  - `httpx` 或 `requests` (API调用)
  - `pypdf` 或 `pdfplumber` (PDF解析，推荐pdfplumber)
  - `rich` (CLI显示，参考deepagents-cli)
  - `prompt-toolkit` (CLI输入处理，参考deepagents-cli)
  - `python-dotenv` (配置管理)
  - `langchain-openai` (模型支持，用于OpenAI和硅基流动)
  - `langchain-anthropic` (Anthropic模型支持)
- 配置 `[project.scripts]` 添加 `hkex` 命令入口

### 2. 实现HKEX API服务 (`services/hkex_api.py`)

根据接口文档实现：

- `HKEXAPIService` 类
- `get_stock_id(stock_code)` - 股票ID查询（处理JSONP响应）
- `search_announcements(stock_id, from_date, to_date, title, ...)` - 公告搜索（数据清理）
- `get_latest_announcements(market, stock_code, ...)` - 最新公告
- `get_categories()` - 分类数据获取
- 处理JSONP响应、数据清理（HTML编码、Unicode转义）、SSL配置
- **返回数据结构**：确保包含 `news_id`、`pdf_url`、`stock_code`、`date_time`、`title`，便于后续缓存管理

### 3. 实现PDF解析服务 (`services/pdf_parser.py`)

- `PDFParserService` 类
- `sanitize_filename(filename)` - 清理文件名中的特殊字符
  - 移除或替换：`/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`
  - 限制文件名长度（超过200字符则截断）
- `format_date_for_filename(date_time_str)` - 格式化日期为YYYY-MM-DD
  - 解析API返回的 `dd/mm/yyyy HH:MM` 格式
- `download_pdf(url, stock_code, date, title, cache_dir)` - 下载PDF（处理SSL、超时）
  - **文件名生成**：`sanitize_filename(f"{date}-{title}.pdf")`
  - **缓存路径**：`/pdf_cache/{stock_code}/{日期-标题}.pdf`
  - **缓存检查**：先检查缓存路径是否存在
  - **存在则返回**：直接返回缓存路径，跳过下载
  - **不存在则下载**：下载后保存到缓存目录
  - **目录创建**：自动创建股票代码目录
- `get_cached_pdf_path(stock_code, date, title, cache_dir)` - 获取缓存的PDF路径（如果存在）
  - 构建路径：`/pdf_cache/{stock_code}/{日期-标题}.pdf`
  - 检查文件是否存在，返回完整路径或None
- `extract_text(pdf_path)` - 提取文本（支持中文）
- `extract_tables(pdf_path)` - 提取表格
- `analyze_structure(pdf_path)` - 分析文档结构（章节、标题等）
- `cleanup_old_pdfs(cache_dir, days=30)` - 清理旧PDF（可选工具）

### 4. 创建DeepAgents工具 (`tools/hkex_tools.py`)

使用 `@tool` 装饰器创建工具：

- `search_hkex_announcements` - 搜索公告（封装API服务）
- `get_latest_hkex_announcements` - 获取最新公告
- `get_stock_info` - 获取股票信息
- `get_announcement_categories` - 获取分类信息
- 工具描述要详细，便于Agent理解使用场景

### 5. 创建PDF处理工具 (`tools/pdf_tools.py`)

- `download_announcement_pdf` - 下载公告PDF（需要HITL审批）
  - **参数**：`news_id`, `pdf_url`, `stock_code`, `date_time`, `title`, `force_download=False`
  - **智能缓存**：先调用 `get_cached_pdf_path()` 检查缓存
  - **缓存命中**：直接返回路径，无需HITL审批
  - **缓存未命中**：下载PDF，需要HITL审批（首次下载）
  - **返回**：PDF本地路径（缓存路径或新下载路径）
- `get_cached_pdf_path` - 获取缓存的PDF路径（如果存在）
  - 供Agent查询缓存状态
- `extract_pdf_content` - 提取PDF内容（文本+表格）
  - 自动从缓存读取，无需重复下载
- `analyze_pdf_structure` - 分析PDF结构
- 大文件结果自动写入文件系统

### 6. 创建主Agent (`agents/main_agent.py`)

- `create_hkex_agent()` 函数
- 配置系统提示词（HKEX公告分析专家角色）
  - **说明PDF缓存机制**：告知Agent优先使用缓存，避免重复下载
- 集成所有HKEX工具和PDF工具
- 配置文件系统后端（CompositeBackend）：
  - `/pdf_cache/` → FilesystemBackend（持久化PDF缓存，root_dir=agent_dir/pdf_cache）
  - `/memories/` → FilesystemBackend（长期记忆，root_dir=agent_dir/memories）
  - 默认 → FilesystemBackend（工作目录）
- 设置Human-in-the-Loop（仅首次PDF下载需要审批，缓存命中无需审批）
- 支持checkpointer持久化状态
- Agent目录：`~/.hkex-agent/{AGENT_NAME}/`

### 7. 创建子Agent (`agents/subagents.py`)

定义专门的子Agent：

- `pdf_analyzer` - PDF内容分析专家
  - 专门处理PDF解析和分析
  - 提取关键信息、生成摘要、识别财务数据
  - 使用PDF工具（自动利用缓存）
- `report_generator` - 报告生成专家
  - 基于分析结果生成结构化报告
  - 支持多种报告格式（Markdown、JSON等）

### 8. 实现CLI (`cli/`)

**充分参考 `libs/deepagents-cli/deepagents_cli/` 的实现**，复用其架构和模式：

- `__main__.py` - CLI入口点（参考 `libs/deepagents-cli/deepagents_cli/__main__.py`）
- `main.py` - CLI主循环（参考 `libs/deepagents-cli/deepagents_cli/main.py`）
  - `cli_main()` - 入口函数，参数解析
  - `main()` - 异步主函数，Agent创建
  - `simple_cli()` - 交互式循环
- `config.py` - 配置和常量（参考 `libs/deepagents-cli/deepagents_cli/config.py`）
  - `create_model()` - 模型创建（支持OpenAI/Anthropic/硅基流动）
  - **硅基流动支持**：
    - 检查 `SILICONFLOW_API_KEY` 环境变量
    - 使用 `ChatOpenAI` 配置 `base_url="https://api.siliconflow.cn/v1"`
    - 支持通过 `SILICONFLOW_MODEL` 环境变量指定模型（如：deepseek-chat, qwen等）
    - 优先级：硅基流动 > OpenAI > Anthropic
  - `COLORS` - 颜色配置
  - `console` - Rich Console实例
- `agent.py` - Agent创建和管理（参考 `libs/deepagents-cli/deepagents_cli/agent.py`）
  - `create_agent_with_config()` - 创建HKEX Agent
  - `get_system_prompt()` - HKEX专用系统提示词（包含PDF缓存说明）
  - Agent目录管理（`~/.hkex-agent/AGENT_NAME/`）
- `tools.py` - 工具定义（参考 `libs/deepagents-cli/deepagents_cli/tools.py`）
  - 集成HKEX工具和PDF工具
- `ui.py` - UI渲染（参考 `libs/deepagents-cli/deepagents_cli/ui.py`）
  - `TokenTracker` - Token使用统计
  - 帮助屏幕、文件操作显示
  - Todo列表可视化
- `input.py` - 输入处理（参考 `libs/deepagents-cli/deepagents_cli/input.py`）
  - 文件上下文注入（`@filename`）
  - Tab补全、提示会话
- `commands.py` - 命令处理（参考 `libs/deepagents-cli/deepagents_cli/commands.py`）
  - `/help`, `/clear`, `/tokens`, `/quit` 等命令
- `execution.py` - 任务执行（参考 `libs/deepagents-cli/deepagents_cli/execution.py`）
  - 流式执行、HITL审批、状态管理
- `token_utils.py` - Token统计（参考 `libs/deepagents-cli/deepagents_cli/token_utils.py`）

**CLI功能特性**：

- 交互式对话模式（主要模式）
- 支持文件上下文注入（`@filename`）
- Human-in-the-Loop审批（仅首次PDF下载，缓存命中无需审批）
- Token使用统计和显示
- Todo列表实时可视化
- 文件操作摘要和Diff查看器
- 命令历史记录

### 9. 实现Python API (`api/client.py`)

提供程序化接口：

- `HKEXAgentClient` 类
- `search_announcements()` - 搜索公告
- `analyze_announcement()` - 分析公告（调用Agent，自动利用PDF缓存）
- `generate_report()` - 生成报告（调用Agent）
- `chat()` - 对话接口（流式和非流式）
- 支持同步和异步接口

### 10. 添加配置和文档

- 创建 `.env.example` 模板（API密钥配置）
  - `OPENAI_API_KEY` - OpenAI API密钥（可选）
  - `ANTHROPIC_API_KEY` - Anthropic API密钥（可选）
  - `SILICONFLOW_API_KEY` - 硅基流动API密钥（可选）
  - `SILICONFLOW_MODEL` - 硅基流动模型名称（可选，默认deepseek-chat）
  - 至少需要配置一个模型供应商的API密钥
- 编写 `README.md` 使用文档
  - PDF缓存机制说明
  - 缓存目录结构说明
  - 缓存清理方法
  - 模型供应商配置说明（包括硅基流动）
- 添加CLI和API使用示例
- 添加Agent系统提示词模板

## 关键技术点

1. **API集成**：根据文档处理JSONP响应、数据清理（HTML编码、Unicode转义）、SSL配置
2. **PDF处理**：支持中文PDF解析，提取文本和表格，处理复杂布局
3. **PDF缓存策略**（核心设计）：

   - **存储位置**：`/pdf_cache/{stock_code}/{日期-标题}.pdf`（基于deepagents文件系统）
   - **文件命名**：`{公告日期}-{公告标题}.pdf`，日期格式YYYY-MM-DD
   - **文件名清理**：移除特殊字符，限制长度
   - **缓存检查**：下载前先检查缓存，存在则直接返回路径
   - **目录结构**：按股票代码组织，便于管理和查找
   - **跨会话持久化**：使用FilesystemBackend确保缓存跨会话保留
   - **HITL优化**：缓存命中无需审批，仅首次下载需要

4. **模型供应商支持**：

   - **硅基流动**：通过OpenAI兼容API接入，优先级最高
   - **OpenAI**：标准OpenAI API
   - **Anthropic**：Claude系列模型
   - 支持通过环境变量灵活切换

5. **Agent设计**：主Agent协调任务，子Agent专门处理PDF分析和报告生成
6. **文件系统**：使用deepagents的文件系统存储分析结果、缓存PDF

   - **CompositeBackend配置**：
     - `/pdf_cache/` → FilesystemBackend（持久化PDF缓存）
     - `/memories/` → FilesystemBackend（长期记忆）
     - 默认 → FilesystemBackend（工作目录）

7. **CLI架构**：完全复用deepagents-cli的架构模式，保持一致性
8. **错误处理**：完善的错误处理和用户提示
9. **HITL审批**：仅首次PDF下载需要用户审批，缓存命中无需审批

## 依赖项

- `deepagents` (workspace，路径：`../deepagents`)
- `httpx` - HTTP客户端（支持SSL配置）
- `pypdf` 或 `pdfplumber` - PDF解析（推荐pdfplumber，表格提取更好）
- `rich` - CLI美化
- `prompt-toolkit` - CLI输入处理
- `python-dotenv` - 环境变量管理
- `langchain-openai` - 模型支持（OpenAI和硅基流动）
- `langchain-anthropic` - Anthropic模型支持