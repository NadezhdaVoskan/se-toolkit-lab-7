"""Command handlers for the LMS bot.

Handlers are pure functions that take input and return text.
They don't depend on Telegram — same function works from --test mode and from Telegram.
"""

from .commands import (
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
