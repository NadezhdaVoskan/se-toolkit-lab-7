"""HTTP client for the LMS backend API."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import httpx

from config import config


class BackendError(RuntimeError):
    """User-facing backend error."""


TIMEOUT_SECONDS = 5.0


def _headers() -> dict[str, str]:
    config.validate_for_lms()
    return {"Authorization": f"Bearer {config.LMS_API_KEY}"}


def _host_port(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.hostname or "backend"
    if parsed.port:
        return f"{host}:{parsed.port}"
    return host


def _format_error(error: Exception) -> BackendError:
    host = _host_port(config.LMS_API_BASE_URL)

    if isinstance(error, httpx.HTTPStatusError):
        status = error.response.status_code
        reason = error.response.reason_phrase or "Unknown Error"
        return BackendError(
            f"Backend error: HTTP {status} {reason}. The backend service may be down."
        )

    if isinstance(error, httpx.ConnectError):
        return BackendError(
            f"Backend error: connection refused ({host}). "
            "Check that the services are running."
        )

    if isinstance(error, httpx.TimeoutException):
        return BackendError(
            f"Backend error: request timed out while contacting {host}. "
            "Check that the backend service is responding."
        )

    return BackendError(f"Backend error: {error}")


def _get(path: str, params: dict[str, str] | None = None) -> Any:
    try:
        with httpx.Client(
            base_url=config.LMS_API_BASE_URL,
            headers=_headers(),
            timeout=TIMEOUT_SECONDS,
            trust_env=False,
        ) as client:
            response = client.get(path, params=params)
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise _format_error(error) from None


def get_items() -> list[dict[str, Any]]:
    """Return LMS items."""
    data = _get("/items/")
    if isinstance(data, list):
        return data
    raise BackendError("Backend error: invalid response from /items/")


def get_pass_rates(lab: str) -> list[dict[str, Any]]:
    """Return pass-rate analytics for a lab."""
    data = _get("/analytics/pass-rates", params={"lab": lab})
    if isinstance(data, list):
        return data
    raise BackendError("Backend error: invalid response from /analytics/pass-rates")
