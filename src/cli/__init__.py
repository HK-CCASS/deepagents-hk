"""HKEX Agent CLI package."""

# Lazy import to avoid circular dependency when using agents module
def cli_main(*args, **kwargs):
    """Lazy loader for cli_main to avoid circular imports."""
    from .main import cli_main as _cli_main
    return _cli_main(*args, **kwargs)

__all__ = ["cli_main"]
