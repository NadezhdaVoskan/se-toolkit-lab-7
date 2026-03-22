"""LLM-powered intent router for plain-text bot messages."""

from __future__ import annotations

import json
import sys
from typing import Any

from services.llm_client import LLMError, run_tool_loop
from services.lms_api import (
    BackendError,
    get_completion_rate,
    get_groups,
    get_items,
    get_learners,
    get_pass_rates,
    get_scores,
    get_timeline,
    get_top_learners,
    trigger_sync,
)
from services.tool_schemas import TOOLS


SYSTEM_PROMPT = """You are an LMS analytics bot for students and instructors.
Use tools whenever real LMS data is needed. Do not invent data.
For greetings or meaningless text, reply briefly and explain what you can help with.
If the request is ambiguous, ask a short clarifying question.
If the answer requires comparing multiple labs or groups, call tools multiple times before answering.
Keep the final answer short, clear, and user-facing."""


TOOL_EXECUTORS = {
    "get_items": lambda arguments: get_items(),
    "get_learners": lambda arguments: get_learners(),
    "get_scores": lambda arguments: get_scores(str(arguments["lab"])),
    "get_pass_rates": lambda arguments: get_pass_rates(str(arguments["lab"])),
    "get_timeline": lambda arguments: get_timeline(str(arguments["lab"])),
    "get_groups": lambda arguments: get_groups(str(arguments["lab"])),
    "get_top_learners": lambda arguments: get_top_learners(
        str(arguments["lab"]),
        int(arguments.get("limit", 5)),
    ),
    "get_completion_rate": lambda arguments: get_completion_rate(str(arguments["lab"])),
    "trigger_sync": lambda arguments: trigger_sync(),
}


def _summarize_result(result: Any) -> str:
    if isinstance(result, list):
        return f"{len(result)} records"
    if isinstance(result, dict):
        return f"{len(result)} fields"
    return "ok"


def _execute_tool(tool_name: str, arguments: dict[str, Any]) -> Any:
    executor = TOOL_EXECUTORS.get(tool_name)
    if executor is None:
        raise LLMError(f"LLM error: unknown tool '{tool_name}'.")

    print(
        f"[tool] LLM called: {tool_name}({json.dumps(arguments, ensure_ascii=True)})",
        file=sys.stderr,
    )
    try:
        result = executor(arguments)
    except BackendError as error:
        result = {"error": str(error)}
    print(f"[tool] Result: {_summarize_result(result)}", file=sys.stderr)
    print("[summary] Feeding 1 tool result back to LLM", file=sys.stderr)
    return result


def route_intent(user_message: str) -> str:
    """Route plain text through the LLM tool-calling loop."""
    try:
        return run_tool_loop(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            tools=TOOLS,
            tool_executor=_execute_tool,
        )
    except LLMError as error:
        return str(error)
