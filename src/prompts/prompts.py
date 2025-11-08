"""港交所智能体的提示词加载工具。"""

from pathlib import Path


def _get_prompts_dir() -> Path:
    """获取提示词目录路径。
    
    Returns:
        提示词目录的路径。
    """
    return Path(__file__).parent


def load_prompt(filename: str) -> str:
    """从文件加载提示词模板。
    
    Args:
        filename: 提示词文件名（例如，"main_system_prompt.md"）。
        
    Returns:
        提示词内容字符串。
        
    Raises:
        FileNotFoundError: 如果提示词文件不存在。
    """
    prompts_dir = _get_prompts_dir()
    prompt_path = prompts_dir / filename
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"提示词文件未找到: {prompt_path}")
    
    return prompt_path.read_text(encoding="utf-8")


def get_main_system_prompt() -> str:
    """获取主要的港交所智能体系统提示词。
    
    Returns:
        主要系统提示词字符串。
    """
    return load_prompt("main_system_prompt.md")


def get_pdf_analyzer_prompt() -> str:
    """获取 PDF 分析器子智能体提示词。
    
    Returns:
        PDF 分析器提示词字符串。
    """
    return load_prompt("pdf_analyzer_prompt.md")


def get_report_generator_prompt() -> str:
    """获取报告生成器子智能体提示词。
    
    Returns:
        报告生成器提示词字符串。
    """
    return load_prompt("report_generator_prompt.md")


def get_longterm_memory_prompt() -> str:
    """获取长期记忆系统提示词模板。
    
    Returns:
        长期记忆提示词模板字符串（包含 {memory_path} 占位符）。
    """
    return load_prompt("longterm_memory_prompt.md")


def get_default_agent_md() -> str:
    """获取默认的 agent.md 内容。
    
    Returns:
        默认 agent.md 内容字符串。
    """
    return load_prompt("default_agent_md.md")

