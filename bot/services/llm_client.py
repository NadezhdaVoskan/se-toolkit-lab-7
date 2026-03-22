"""LLM client with tool-calling support for intent routing."""

from __future__ import annotations

import json
from typing import Any

import httpx

from config import config


class LLMError(RuntimeError):
    """User-facing LLM error."""


MAX_TOOL_ROUNDS = 8
POST_TOOL_FOLLOW_UP = (
    "Continue from the tool results. "
    "Do not describe plans or say that you will check something. "
    "Either call the next tool immediately, or give the final user-facing answer now."
)

NON_FINAL_PHRASES = (
    "i will call a tool",
    "let me check",
    "i need to check",
    "i'll check",
    "i will check",
    "let me look",
    "i need more data",
)


def _headers() -> dict[str, str]:
    if not config.LLM_API_KEY:
        raise LLMError("LLM error: LLM_API_KEY not set in .env.bot.secret")
    return {
        "Authorization": f"Bearer {config.LLM_API_KEY}",
        "Content-Type": "application/json",
    }


def _format_error(error: Exception) -> LLMError:
    if isinstance(error, httpx.HTTPStatusError):
        status = error.response.status_code
        reason = error.response.reason_phrase or "Unknown Error"
        return LLMError(f"LLM error: HTTP {status} {reason}.")
    if isinstance(error, httpx.ConnectError):
        return LLMError("LLM error: connection refused. Check that the LLM service is running.")
    if isinstance(error, httpx.TimeoutException):
        return LLMError("LLM error: request timed out.")
    return LLMError(f"LLM error: {error}")


def _chat_completion(messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {
        "model": config.LLM_API_MODEL,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
    }

    try:
        with httpx.Client(
            base_url=config.LLM_API_BASE_URL,
            headers=_headers(),
            timeout=30.0,
            trust_env=False,
        ) as client:
            response = client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise _format_error(error) from None

    try:
        return data["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        raise LLMError("LLM error: invalid response format from chat completions API.") from None


def run_tool_loop(
    *,
    system_prompt: str,
    user_message: str,
    tools: list[dict[str, Any]],
    tool_executor,
) -> str:
    """Run the LLM tool-calling loop until a final text answer is produced."""
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    used_tools = False

    for _ in range(MAX_TOOL_ROUNDS):
        message = _chat_completion(messages, tools)
        assistant_message: dict[str, Any] = {"role": "assistant"}

        if message.get("content"):
            assistant_message["content"] = message["content"]

        tool_calls = message.get("tool_calls") or []
        if tool_calls:
            used_tools = True
            assistant_message["tool_calls"] = tool_calls
            messages.append(assistant_message)

            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                arguments_raw = tool_call["function"].get("arguments") or "{}"
                try:
                    arguments = json.loads(arguments_raw)
                except json.JSONDecodeError:
                    arguments = {}

                result = tool_executor(tool_name, arguments)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": tool_name,
                        "content": json.dumps(result, ensure_ascii=True),
                    }
                )
            continue

        content = message.get("content")
        if isinstance(content, str) and content.strip():
            normalized_content = content.strip().lower()
            if used_tools:
                messages.append({"role": "assistant", "content": content.strip()})
                messages.append({"role": "user", "content": POST_TOOL_FOLLOW_UP})
                used_tools = False
                continue
            if any(phrase in normalized_content for phrase in NON_FINAL_PHRASES):
                messages.append({"role": "assistant", "content": content.strip()})
                messages.append({"role": "user", "content": POST_TOOL_FOLLOW_UP})
                continue
            return content.strip()

    raise LLMError("LLM error: tool loop exceeded the maximum number of steps.")
