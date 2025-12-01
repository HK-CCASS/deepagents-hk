"""HKEX Agent CLI package.

Note: We avoid importing cli_main here to prevent circular imports.
Use 'from src.cli.main import cli_main' directly when needed.
"""

# Expose only what's safe to import without circular dependencies
from .agent_memory import AgentMemoryMiddleware
from .project_utils import find_project_root

__all__ = ["AgentMemoryMiddleware", "find_project_root"]
