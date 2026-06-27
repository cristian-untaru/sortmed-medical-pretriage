"""Data models returned by the input guard."""

from __future__ import annotations

from dataclasses import dataclass, field


# Carries the guard decision and enough metadata for debugging/tests.
@dataclass(frozen=True)
class InputGuardResult:
    allowed: bool
    message: str = ""
    intent: str | None = None
    confidence: float | None = None
    reason: str = ""
    scores: dict[str, float] = field(default_factory=dict)
