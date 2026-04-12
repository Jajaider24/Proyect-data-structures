from __future__ import annotations

from typing import Any, Optional


class ApiBridgeError(Exception):
    """Handling HTTP errors and network failures."""

    def __init__(self, status_code: int, detail: str, payload: Optional[Any] = None) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.payload = payload
