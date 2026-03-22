#!/usr/bin/env python3
"""LMS Telegram Bot entry point."""

import argparse
import sys

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from handlers.core import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_start,
    handle_unknown,
)
from services.intent_router import route_intent


START_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Labs", callback_data="/labs"),
            InlineKeyboardButton("Health", callback_data="/health"),
        ],
        [
            InlineKeyboardButton(
                "Top learners",
                callback_data="who are the top 5 students in lab 4",
            ),
            InlineKeyboardButton(
                "Lowest pass rate",
                callback_data="which lab has the lowest pass rate",
            ),
        ],
    ]
)


def route_command(command_str: str) -> str:
    """Route a slash command or plain-text message to the right handler."""
    command_str = command_str.strip()
    if not command_str:
        return handle_unknown(command_str)

    if not command_str.startswith("/"):
        return route_intent(command_str)

    parts = command_str.split(maxsplit=1)
    command = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if command == "/start":
        return handle_start()
    if command == "/help":
        return handle_help()
    if command == "/health":
        return handle_health()
    if command == "/labs":
        return handle_labs()
    if command == "/scores":
        return handle_scores(arg)
    return handle_unknown(command_str)


def test_mode(command: str) -> None:
    """Run a single command in test mode."""
    print(route_command(command))
    raise SystemExit(0)


def telegram_mode() -> None:
    """Start the Telegram bot."""
    try:
        from config import config

        config.validate_for_telegram()
        print("Starting Telegram bot...")
        print("Bot is running. Send /start to your bot in Telegram.")
        print(f"Inline keyboard configured with {len(START_KEYBOARD.inline_keyboard)} rows.")
        print("Telegram mode not yet implemented. Use --test mode for now.")
        raise SystemExit(1)
    except ValueError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        raise SystemExit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LMS Telegram Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  uv run bot.py --test \"/start\"\n"
            "  uv run bot.py --test \"what labs are available\"\n"
            "  uv run bot.py                    # Telegram mode"
        ),
    )
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run a single command in test mode",
    )

    args = parser.parse_args()
    if args.test:
        test_mode(args.test)
    telegram_mode()


if __name__ == "__main__":
    main()
