from typing import Any

from pydantic import BaseModel


class ScopeClassificationResult(BaseModel):
    scope_checked: bool = True
    scope_provider: str
    scope_available: bool
    scope_allowed: bool
    scope_reason: str | None = None
    scope_intent: str | None = None
    scope_source_group: str | None = None
    scope_raw_response: str | None = None

    def to_metadata(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)
