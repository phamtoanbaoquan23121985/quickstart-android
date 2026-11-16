"""Boundary Conservation Law with explicit, evidence-bearing delegation."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Authority:
    level: int
    capabilities: frozenset[str]

@dataclass(frozen=True)
class AuthorityEdge:
    source: Authority
    target: Authority
    delegated_capabilities: frozenset[str] = frozenset()
    delegation_evidence: str | None = None

@dataclass(frozen=True)
class AuthorityFlowResult:
    allowed: bool
    unauthorized_capabilities: tuple[str, ...]
    reasons: tuple[str, ...]

def validate_authority_flow(edges: list[AuthorityEdge]) -> AuthorityFlowResult:
    """Reject privilege/capability growth unless explicitly and narrowly delegated."""
    violations, reasons = set(), []
    for index, edge in enumerate(edges):
        gained, delegated = set(edge.target.capabilities) - set(edge.source.capabilities), set(edge.delegated_capabilities)
        if delegated and not edge.delegation_evidence:
            violations.update(gained)
            reasons.append(f"edge[{index}]: delegation has no evidence")
            continue
        unauthorized = gained - delegated
        if unauthorized:
            violations.update(unauthorized)
            reasons.append(f"edge[{index}]: capabilities increased without delegation")
        if edge.target.level > edge.source.level and not edge.delegation_evidence:
            reasons.append(f"edge[{index}]: authority level increased without delegation evidence")
    return AuthorityFlowResult(not violations and not reasons, tuple(sorted(violations)), tuple(reasons))
