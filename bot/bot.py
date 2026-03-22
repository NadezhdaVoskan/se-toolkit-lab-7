#!/usr/bin/env python3
"""LMS Telegram Bot entry point."""

from __future__ import annotations

import argparse
import sys

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TimedOut
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ExtBot,
    MessageHandler,
    filters,
)
from telegram.request import HTTPXRequest

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


async def _safe_reply_text(
    update: Update,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Send a Telegram reply with a retry and a plain-text fallback."""
    message = update.effective_message
    if message is None:
        return

    try:
        await message.reply_text(text, reply_markup=reply_markup)
        return
    except TimedOut:
        pass

    try:
        await message.reply_text(text, reply_markup=reply_markup)
        return
    except TimedOut:
        pass

    if reply_markup is not None:
        await message.reply_text(text)


async def _send_start(update: Update) -> None:
    await _safe_reply_text(update, handle_start(), reply_markup=START_KEYBOARD)


async def _handle_start_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Reply to /start with inline buttons."""
    del context
    await _send_start(update)


async def _handle_help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Reply to /help."""
    del context
    await _safe_reply_text(update, handle_help())


async def _handle_health_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Reply to /health."""
    del context
    await _safe_reply_text(update, handle_health())


async def _handle_labs_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Reply to /labs."""
    del context
    await _safe_reply_text(update, handle_labs())


async def _handle_scores_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Reply to /scores with an optional lab argument."""
    lab = " ".join(context.args)
    await _safe_reply_text(update, handle_scores(lab))


async def _handle_text_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Route plain text through the existing intent router."""
    del context
    message = update.effective_message
    if message is None or message.text is None:
        return
    await _safe_reply_text(update, route_command(message.text))


async def _handle_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle inline button presses by routing callback text."""
    del context
    query = update.callback_query
    if query is None or query.data is None:
        return

    await query.answer()
    if query.data == "/start":
        await _send_start(update)
        return

    await _safe_reply_text(update, route_command(query.data))


def telegram_mode() -> None:
    """Start the Telegram bot with long polling."""
    try:
        from config import config

        config.validate_for_telegram()
        print("Starting Telegram bot...")
        print("Bot is running. Send /start to your bot in Telegram.")
        print(
            f"Inline keyboard configured with {len(START_KEYBOARD.inline_keyboard)} rows."
        )

        request = HTTPXRequest(
            connection_pool_size=8,
            connect_timeout=30.0,
            read_timeout=30.0,
            write_timeout=30.0,
            pool_timeout=30.0,
        )
        bot = ExtBot(token=config.BOT_TOKEN, request=request)
        application = Application.builder().bot(bot).build()
        application.add_handler(CommandHandler("start", _handle_start_command))
        application.add_handler(CommandHandler("help", _handle_help_command))
        application.add_handler(CommandHandler("health", _handle_health_command))
        application.add_handler(CommandHandler("labs", _handle_labs_command))
        application.add_handler(CommandHandler("scores", _handle_scores_command))
        application.add_handler(CallbackQueryHandler(_handle_callback))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_text_message)
        )
        application.run_polling()
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
