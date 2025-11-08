"""HKEX Agent CLI package."""

# Install editable finder before importing to ensure correct package resolution
# This fixes the issue where clibuilder's cli.py conflicts with our cli package
import sys
try:
    import __editable___hkex_agent_0_1_0_finder
    finder_instance = __editable___hkex_agent_0_1_0_finder._EditableFinder()
    # Insert at the beginning to take precedence over other finders
    if not any(isinstance(f, __editable___hkex_agent_0_1_0_finder._EditableFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, finder_instance)
except ImportError:
    pass  # Not an editable install, skip

from cli.main import cli_main

__all__ = ["cli_main"]
