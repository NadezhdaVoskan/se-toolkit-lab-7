"""Handler functions for Telegram commands."""

from __future__ import annotations

from services.lms_api import BackendError, get_items, get_pass_rates


def _extract_lab_titles(items: list[dict[str, object]]) -> list[str]:
    return [
        str(item.get("title", "")).strip()
        for item in items
        if str(item.get("type", "")).lower() == "lab" and str(item.get("title", "")).strip()
    ]


def _format_lab_label(lab: str) -> str:
    normalized = lab.strip().lower()
    if normalized.startswith("lab-"):
        suffix = normalized.removeprefix("lab-")
        if suffix.isdigit():
            return f"Lab {suffix.zfill(2)}"
    return lab.strip()


def handle_start() -> str:
    """Handler for /start command."""
    return (
        "Welcome to the LMS Bot.\n\n"
        "I can help you check labs, scores, and backend status.\n"
        "Type /help to see all available commands."
    )


def handle_help() -> str:
    """Handler for /help command."""
    return (
        "Available commands:\n\n"
        "/start - Welcome message\n"
        "/help - List available commands\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab> - View pass rates for a lab"
    )


def handle_health() -> str:
    """Handler for /health command."""
    try:
        items = get_items()
    except BackendError as error:
        return str(error)

    return f"Backend is healthy. {len(items)} items available."


def handle_labs() -> str:
    """Handler for /labs command."""
    try:
        labs = _extract_lab_titles(get_items())
    except BackendError as error:
        return str(error)

    if not labs:
        return "Available labs:\n- No labs found."

    lines = ["Available labs:"]
    lines.extend(f"- {lab}" for lab in labs)
    return "\n".join(lines)


def handle_scores(lab: str) -> str:
    """Handler for /scores command."""
    lab = lab.strip()
    if not lab:
        return "Usage: /scores <lab>\nExample: /scores lab-04"

    try:
        pass_rates = get_pass_rates(lab)
    except BackendError as error:
        return str(error)

    lab_label = _format_lab_label(lab)
    if not pass_rates:
        return f"No pass-rate data found for {lab_label}."

    lines = [f"Pass rates for {lab_label}:"]
    for item in pass_rates:
        task = str(item.get("task", "Unknown task"))
        avg_score = float(item.get("avg_score", 0.0))
        attempts = int(item.get("attempts", 0))
        lines.append(f"- {task}: {avg_score:.1f}% ({attempts} attempts)")
    return "\n".join(lines)


def handle_unknown(text: str) -> str:
    """Handler for unknown commands or plain text."""
    return "Unknown command. Try /help to see what I can do."
