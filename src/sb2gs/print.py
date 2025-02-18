try:
    from rich import print as _print

except ImportError:
    from builtins import print as _print

print = _print

__all__ = ["print"]
