"""Core command handlers for the LMS bot.

Pure functions that map Telegram commands to responses.
No Telegram dependencies — testable from CLI and unit tests.
"""

from .basic import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_start,
    handle_unknown,
)

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "handle_unknown",
]
