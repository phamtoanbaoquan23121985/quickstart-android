"""Mandatory promotion path: every discovery is classified by the REALITY GATE."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from reality_gate import Evidence, FindingStatus, GateResult, evaluate_reality_gate
from sif import fingerprint


@dataclass(frozen=True)
class DiscoveryAssessment:
    observation_fingerprint: str
    status: FindingStatus
    reportable: bool
    confirmed_vulnerability: bool
    gate_reasons: tuple[str, ...]


def assess_discovery(observation: dict[str, Any], evidence: Evidence) -> DiscoveryAssessment:
    """Fingerprint a safe observation and require gate evaluation before any promotion."""
    gate: GateResult = evaluate_reality_gate(evidence)
    return DiscoveryAssessment(
        observation_fingerprint=fingerprint(observation),
        status=gate.status,
        reportable=gate.reportable,
        # This engine never self-confirms a vulnerability; vendor/independent triage is required.
        confirmed_vulnerability=False,
        gate_reasons=gate.reasons,
    )
