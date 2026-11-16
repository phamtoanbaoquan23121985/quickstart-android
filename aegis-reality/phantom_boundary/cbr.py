"""Cross-Boundary Replay: deterministic one-factor-at-a-time experiments."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Experiment:
    identity: str
    authority: str
    payload: str

def build_one_factor_replays(baseline: Experiment, alternatives: dict[str, list[str]]) -> list[Experiment]:
    """Each replay differs from baseline in exactly one dimension."""
    allowed = {"identity", "authority", "payload"}
    unknown = set(alternatives) - allowed
    if unknown: raise ValueError(f"Unknown experiment dimensions: {', '.join(sorted(unknown))}")
    replays = []
    for field in ("identity", "authority", "payload"):
        for value in alternatives.get(field, []):
            if not isinstance(value, str) or not value: raise ValueError(f"Invalid value for {field}")
            if value != getattr(baseline, field):
                replays.append(Experiment(**{name: value if name == field else getattr(baseline, name)
                                             for name in ("identity", "authority", "payload")}))
    return replays

def compare_outcomes(baseline: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    """Return changed observable paths; do not infer exploitability."""
    from sif import compare_fingerprints
    return compare_fingerprints(baseline, candidate)
