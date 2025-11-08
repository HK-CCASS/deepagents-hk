"""Sub-agent definitions for HKEX announcement analysis."""

from typing import Any

from prompts.prompts import (
    get_pdf_analyzer_prompt,
    get_report_generator_prompt,
)
from tools.hkex_tools import (
    get_announcement_categories,
    get_latest_hkex_announcements,
    get_stock_info,
    search_hkex_announcements,
)
from tools.pdf_tools import (
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

    Returns:
        Subagent configuration dictionary.
    """
    return {
        "name": "pdf-analyzer",
        "description": (
            "Specialized agent for analyzing PDF announcement content. "
            "Use this when you need to extract and analyze text, tables, "
            "or structure from PDF files."
        ),
        "system_prompt": get_pdf_analyzer_prompt(),
        "tools": PDF_ANALYZER_TOOLS,
    }


def get_report_generator_subagent() -> dict[str, Any]:
    """Get report generator subagent configuration.

    This subagent specializes in generating structured reports based on
    announcement analysis results.

    Returns:
        Subagent configuration dictionary.
    """
    return {
        "name": "report-generator",
        "description": (
            "Specialized agent for generating structured reports from announcement analysis. "
            "Use this when you need to create comprehensive reports, summaries, or "
            "structured output based on announcement data and analysis."
        ),
        "system_prompt": get_report_generator_prompt(),
        "tools": REPORT_GENERATOR_TOOLS,
    }


def get_all_subagents() -> list[dict[str, Any]]:
    """Get all subagent configurations.

    Returns:
        List of subagent configuration dictionaries.
    """
    return [
        get_pdf_analyzer_subagent(),
        get_report_generator_subagent(),
    ]

