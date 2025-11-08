"""Sub-agent definitions for HKEX announcement analysis."""

from typing import Any

from src.config.agent_config import agent_model_config
from src.prompts.prompts import (
    get_pdf_analyzer_prompt,
    get_report_generator_prompt,
)
from src.tools.hkex_tools import (
    get_announcement_categories,
    get_latest_hkex_announcements,
    get_stock_info,
    search_hkex_announcements,
)
from src.tools.pdf_tools import (
    analyze_pdf_structure,
    extract_pdf_content,
    get_cached_pdf_path,
)

# PDF analyzer subagent tools
PDF_ANALYZER_TOOLS = [
    get_cached_pdf_path,
    extract_pdf_content,
    analyze_pdf_structure,
]

# Report generator subagent tools (has access to all tools)
REPORT_GENERATOR_TOOLS = [
    search_hkex_announcements,
    get_latest_hkex_announcements,
    get_stock_info,
    get_announcement_categories,
    get_cached_pdf_path,
    extract_pdf_content,
    analyze_pdf_structure,
]


def get_pdf_analyzer_subagent() -> dict[str, Any]:
    """Get PDF analyzer subagent configuration.

    This subagent specializes in analyzing PDF announcement content.
    It extracts text, tables, and structure from PDFs.
    
    Uses a lightweight model (Qwen2.5-7B-Instruct) for cost optimization.
    Can be configured via SILICONFLOW_PDF_MODEL environment variable.

    Returns:
        Subagent configuration dictionary.
    """
    config = {
        "name": "pdf-analyzer",
        "description": (
            "Specialized agent for analyzing PDF announcement content. "
            "Use this when you need to extract and analyze text, tables, "
            "or structure from PDF files."
        ),
        "system_prompt": get_pdf_analyzer_prompt(),
        "tools": PDF_ANALYZER_TOOLS,
    }
    
    # 如果配置了独立模型，创建独立的模型实例
    if agent_model_config.pdf_analyzer_model:
        try:
            # 使用PDF分析专用温度（如果配置）
            temp = agent_model_config.pdf_analyzer_temperature
            config["model"] = agent_model_config.create_model_instance(
                agent_model_config.pdf_analyzer_model,
                temperature=temp
            )
        except ValueError:
            # API密钥未配置，使用默认模型
            pass
    
    return config


def get_report_generator_subagent() -> dict[str, Any]:
    """Get report generator subagent configuration.

    This subagent specializes in generating structured reports based on
    announcement analysis results.
    
    Uses a high-quality model (Qwen2.5-72B-Instruct) for better output.
    Can be configured via SILICONFLOW_REPORT_MODEL environment variable.

    Returns:
        Subagent configuration dictionary.
    """
    config = {
        "name": "report-generator",
        "description": (
            "Specialized agent for generating structured reports from announcement analysis. "
            "Use this when you need to create comprehensive reports, summaries, or "
            "structured output based on announcement data and analysis."
        ),
        "system_prompt": get_report_generator_prompt(),
        "tools": REPORT_GENERATOR_TOOLS,
    }
    
    # 如果配置了独立模型，创建独立的模型实例
    if agent_model_config.report_generator_model:
        try:
            # 使用报告生成专用温度（如果配置）
            temp = agent_model_config.report_generator_temperature
            config["model"] = agent_model_config.create_model_instance(
                agent_model_config.report_generator_model,
                temperature=temp
            )
        except ValueError:
            # API密钥未配置，使用默认模型
            pass
    
    return config


def get_all_subagents() -> list[dict[str, Any]]:
    """Get all subagent configurations.

    Returns:
        List of subagent configuration dictionaries.
    """
    return [
        get_pdf_analyzer_subagent(),
        get_report_generator_subagent(),
    ]

