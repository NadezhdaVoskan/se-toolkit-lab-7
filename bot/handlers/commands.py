"""Handler functions for Telegram commands.

Each handler takes input (command name, arguments) and returns text.
No Telegram dependencies — handlers can be called from --test mode or tests.
"""


def handle_start() -> str:
    """Handler for /start command — welcome message."""
    return (
        "👋 Welcome to the LMS Bot!\n\n"
        "I can help you check labs, scores, and system status.\n"
        "Type /help to see all available commands."
    )


def handle_help() -> str:
    """Handler for /help command — lists all available commands."""
    return (
        "📋 Available commands:\n\n"
        "/start — Welcome message\n"
        "/help — This message\n"
        "/health — Check backend status\n"
        "/labs — List available labs\n"
        "/scores <lab> — View scores for a lab\n\n"
        "You can also ask questions in plain text (Task 3)."
    )


def handle_health() -> str:
    """Handler for /health command — backend status.
    
    Returns placeholder for now. Task 2 will query the backend.
    """
    return "🏥 Backend status: Not implemented yet"


def handle_labs() -> str:
    """Handler for /labs command — list available labs.
    
    Returns placeholder for now. Task 2 will query the backend.
    """
    return "📚 Available labs: Not implemented yet"


def handle_scores(lab: str) -> str:
    """Handler for /scores command — view scores for a lab.
    
    Args:
        lab: Lab identifier (e.g., "lab-04")
    
    Returns:
        Scores summary (placeholder for now).
    """
    if not lab.strip():
        return "❌ Usage: /scores <lab>\nExample: /scores lab-04"
    return f"📊 Scores for {lab}: Not implemented yet"


def handle_unknown(text: str) -> str:
    """Handler for unknown commands or plain text.
    
    Args:
        text: User input
    
    Returns:
        Default response (placeholder for now).
    """
    return (
        "🤔 I didn't understand that.\n"
        "Try /help to see what I can do, or ask me about labs and scores."
    )
