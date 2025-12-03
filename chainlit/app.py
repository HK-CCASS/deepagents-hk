"""
HKEX Agent - Chainlit Web Interface

港股智能分析系统 Web 界面，基于 Chainlit 构建。
支持对话历史持久化和恢复。
"""

import os
import sys
from pathlib import Path
from typing import Optional

# 获取项目根目录
project_root = Path(__file__).parent.parent.resolve()

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(project_root))

# 切换工作目录到项目根目录，确保相对路径正确解析
# 这样 mcp_config.json、pdf_cache/ 等路径都能正常工作
os.chdir(project_root)

import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage

from src.cli.config import create_model
from src.agents.main_agent import create_hkex_agent

# ============== 数据持久化配置 ==============
# 使用 SQLite 存储对话历史
DB_PATH = project_root / "chainlit_data" / "chat_history.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


@cl.data_layer
def get_data_layer():
    """配置 SQLite 数据持久化层。"""
    return SQLAlchemyDataLayer(
        conninfo=f"sqlite+aiosqlite:///{DB_PATH}",
        auto_upgrade=True,  # 自动创建/升级数据库表
    )


# ============== 简单用户认证 ==============
@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    """
    简单密码认证。
    
    默认用户：
    - 用户名: admin, 密码: admin (管理员)
    - 用户名: user, 密码: user (普通用户)
    
    可以通过环境变量 CHAINLIT_AUTH_SECRET 设置自定义密钥。
    """
    # 简单的用户验证（生产环境应使用更安全的方式）
    users = {
        "admin": {"password": "admin", "role": "admin"},
        "user": {"password": "user", "role": "user"},
    }
    
    if username in users and users[username]["password"] == password:
        return cl.User(
            identifier=username,
            metadata={"role": users[username]["role"], "provider": "credentials"}
        )
    return None


# ============== 对话恢复 ==============
@cl.on_chat_resume
async def on_chat_resume(thread: dict):
    """恢复历史对话时的处理。"""
    # 创建模型和 Agent
    try:
        model = create_model()
        enable_mcp = os.getenv("ENABLE_MCP", "false").lower() == "true"
        
        agent = await create_hkex_agent(
            model=model,
            assistant_id=thread["id"],
            enable_mcp=enable_mcp,
        )
        
        cl.user_session.set("agent", agent)
        cl.user_session.set("thread_id", thread["id"])
        
        await cl.Message(
            content=f"📂 已恢复对话: **{thread.get('name', '未命名对话')}**\n\n继续您的分析..."
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ **恢复对话失败**\n\n```\n{str(e)}\n```"
        ).send()


@cl.on_chat_start
async def on_chat_start():
    """初始化聊天会话，创建 HKEX Agent。"""
    # 发送欢迎消息
    await cl.Message(
        content="🏛️ **港股智能分析系统** 已就绪！\n\n"
                "我可以帮助您：\n"
                "- 📰 搜索和分析港交所公告\n"
                "- 📄 解析 PDF 文档\n"
                "- 📊 生成分析报告\n"
                "- 💹 查询股票信息\n\n"
                "请输入您的问题或指令开始分析。"
    ).send()

    # 创建模型
    try:
        model = create_model()
    except Exception as e:
        await cl.Message(
            content=f"❌ **模型初始化失败**\n\n请检查 API 密钥配置：\n```\n{str(e)}\n```"
        ).send()
        return

    # 检查是否启用 MCP
    enable_mcp = os.getenv("ENABLE_MCP", "false").lower() == "true"

    # 创建 HKEX Agent
    try:
        agent = await create_hkex_agent(
            model=model,
            assistant_id=cl.context.session.id,
            enable_mcp=enable_mcp,
        )
        # 保存到用户会话
        cl.user_session.set("agent", agent)
        cl.user_session.set("thread_id", cl.context.session.id)
        
        if enable_mcp:
            await cl.Message(content="🔌 MCP 集成已启用").send()
            
    except Exception as e:
        await cl.Message(
            content=f"❌ **Agent 创建失败**\n\n```\n{str(e)}\n```"
        ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """处理用户消息。"""
    agent = cl.user_session.get("agent")
    thread_id = cl.user_session.get("thread_id")

    if not agent:
        await cl.Message(
            content="⚠️ Agent 未初始化，请刷新页面重试。"
        ).send()
        return

    # 配置
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    # 创建响应消息
    response_msg = cl.Message(content="")
    await response_msg.send()

    try:
        # 流式处理 Agent 响应
        full_response = ""
        tool_calls_info = []

        async for event in agent.astream(
            {"messages": [HumanMessage(content=message.content)]},
            config=config,
            stream_mode="messages",
        ):
            msg, metadata = event
            
            # 处理 AI 消息内容
            if hasattr(msg, 'content') and msg.content:
                if isinstance(msg, AIMessage) or metadata.get("langgraph_node") in ["agent", "final"]:
                    # 流式输出 token
                    await response_msg.stream_token(msg.content)
                    full_response += msg.content

            # 收集工具调用信息
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_calls_info.append({
                        "name": tool_call.get("name", "unknown"),
                        "args": tool_call.get("args", {}),
                    })

        # 如果有工具调用，显示工具使用信息
        if tool_calls_info:
            tools_used = ", ".join([t["name"] for t in tool_calls_info])
            await cl.Message(
                content=f"🔧 *使用工具: {tools_used}*",
                author="system",
            ).send()

        # 更新最终消息
        if full_response:
            response_msg.content = full_response
            await response_msg.update()
        else:
            response_msg.content = "✅ 任务已完成"
            await response_msg.update()

    except Exception as e:
        error_msg = f"❌ **处理出错**\n\n```\n{str(e)}\n```"
        response_msg.content = error_msg
        await response_msg.update()


@cl.on_stop
async def on_stop():
    """处理用户停止请求。"""
    await cl.Message(content="⏹️ 已停止当前任务").send()


# 处理人机交互审批
@cl.action_callback("approve")
async def on_action_approve(action: cl.Action):
    """处理工具审批。"""
    await cl.Message(content="✅ 已批准执行").send()
    return "approve"


@cl.action_callback("reject")
async def on_action_reject(action: cl.Action):
    """处理工具拒绝。"""
    await cl.Message(content="❌ 已拒绝执行").send()
    return "reject"

