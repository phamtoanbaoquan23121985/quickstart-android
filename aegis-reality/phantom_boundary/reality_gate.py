"""Fail-closed REALITY GATE; passing permits triage, never auto-confirms a vulnerability."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class FindingStatus(str, Enum):
    REJECTED = "REJECTED"
    CANDIDATE = "CANDIDATE"
    REPORTABLE = "REPORTABLE"

@dataclass(frozen=True)
class Evidence:
    device_codename: str
    api_level: int
    physical_device: bool
    scope_authorized: bool
    repeatable: bool
    invariant_violated: bool
    platform_attribution: bool
    safe_poc: bool
    independent_review: bool
    evidence_class: str

@dataclass(frozen=True)
class GateResult:
    status: FindingStatus
    reportable: bool
    confirmed_vulnerability: bool
    reasons: tuple[str, ...]

_ALLOWED_DEVICES = {"blazer", "mustang"}

def evaluate_reality_gate(evidence: Evidence) -> GateResult:
    """Only approved physical Pixel API 36 + direct OBSERVED evidence can be REPORTABLE."""
    hard = []
    if evidence.device_codename not in _ALLOWED_DEVICES: hard.append("device is outside approved Pixel 10 Pro/XL set")
    if evidence.api_level != 36: hard.append("Android API level is not 36")
    if not evidence.physical_device: hard.append("evidence is not from a physical device")
    if not evidence.scope_authorized: hard.append("program scope/authorization is not established")
    if hard: return GateResult(FindingStatus.REJECTED, False, False, tuple(hard))
    missing = []
    for field, label in (
        ("repeatable", "reproduction is not repeatable"),
        ("invariant_violated", "no security invariant violation is demonstrated"),
        ("platform_attribution", "platform-level attribution is not established"),
        ("safe_poc", "safe, non-destructive PoC is not established"),
        ("independent_review", "independent evidence review is incomplete"),
    ):
        if not getattr(evidence, field): missing.append(label)
    if evidence.evidence_class != "OBSERVED": missing.append("evidence is not direct OBSERVED device evidence")
    if missing: return GateResult(FindingStatus.CANDIDATE, False, False, tuple(missing))
    # REPORTABLE means eligible for human/program triage, not vendor confirmation or reward.
    return GateResult(FindingStatus.REPORTABLE, True, False, ())
