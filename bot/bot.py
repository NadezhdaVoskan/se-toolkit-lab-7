#!/usr/bin/env python3
"""LMS Telegram Bot — Entry point.

Supports two modes:
  1. --test mode: Test handlers without Telegram (CLI)
  2. Telegram mode: Run as a Telegram bot

Usage:
  uv run bot.py --test "/start"
  uv run bot.py --test "/help"
  uv run bot.py                    # Telegram mode
"""

import argparse
import sys
from pathlib import Path

from handlers.core import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_start,
    handle_unknown,
)


def route_command(command_str: str) -> str:
    """Route a command string to the appropriate handler.
    
    Args:
        command_str: User input (e.g., "/start", "/help", "/scores lab-04")
    
    Returns:
        Handler response as a string.
    """
    # Remove leading/trailing whitespace
    command_str = command_str.strip()
    
    # Parse command and arguments
    parts = command_str.split(maxsplit=1)
    if not parts:
        return handle_unknown(command_str)
    
    command = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""
    
    # Route to appropriate handler
    if command == "/start":
        return handle_start()
    elif command == "/help":
        return handle_help()
    elif command == "/health":
        return handle_health()
    elif command == "/labs":
        return handle_labs()
    elif command == "/scores":
        return handle_scores(arg)
    else:
        return handle_unknown(command_str)


def test_mode(command: str) -> None:
    """Run a single command in test mode (no Telegram connection).
    
    Args:
        command: Command string (e.g., "/start")
    """
    response = route_command(command)
    print(response)
    sys.exit(0)


def telegram_mode() -> None:
    """Start the Telegram bot (full mode)."""
    try:
        from config import config
        
        config.validate_for_telegram()
        print("🤖 Starting Telegram bot...")
        print(f"Bot is running. Send /start to your bot in Telegram.")
        # Minimal placeholder — full implementation in Task 2
        print("⚠️  Telegram mode not yet implemented. Use --test mode for now.")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LMS Telegram Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  uv run bot.py --test \"/start\"\n"
            "  uv run bot.py --test \"/help\"\n"
            "  uv run bot.py                    # Telegram mode"
        ),
    )
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run a single command in test mode (no Telegram)",
    )
    
    args = parser.parse_args()
    
    if args.test:
        test_mode(args.test)
    else:
        telegram_mode()


if __name__ == "__main__":
    main()
