"""Prompt loading utilities for HKEX agent."""

from pathlib import Path


def _get_prompts_dir() -> Path:
    """Get the prompts directory path.
    
    Returns:
        Path to the prompts directory.
    """
    return Path(__file__).parent


def load_prompt(filename: str) -> str:
    """Load a prompt template from a file.
    
    Args:
        filename: Name of the prompt file (e.g., "main_system_prompt.md").
        
    Returns:
        Prompt content as string.
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist.
    """
    prompts_dir = _get_prompts_dir()
    prompt_path = prompts_dir / filename
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    return prompt_path.read_text(encoding="utf-8")


def get_main_system_prompt() -> str:
    """Get the main HKEX agent system prompt.
    
    Returns:
        Main system prompt string.
    """
    return load_prompt("main_system_prompt.md")


def get_pdf_analyzer_prompt() -> str:
    """Get the PDF analyzer subagent prompt.
    
    Returns:
        PDF analyzer prompt string.
    """
    return load_prompt("pdf_analyzer_prompt.md")


def get_report_generator_prompt() -> str:
    """Get the report generator subagent prompt.
    
    Returns:
        Report generator prompt string.
    """
    return load_prompt("report_generator_prompt.md")


def get_longterm_memory_prompt() -> str:
    """Get the long-term memory system prompt template.
    
    Returns:
        Long-term memory prompt template string (contains {memory_path} placeholder).
    """
    return load_prompt("longterm_memory_prompt.md")


def get_default_agent_md() -> str:
    """Get the default agent.md content.
    
    Returns:
        Default agent.md content string.
    """
    return load_prompt("default_agent_md.md")

