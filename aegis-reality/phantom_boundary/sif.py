"""Security Invariant Fingerprinting (SIF): canonical, privacy-safe structure diffs."""
from __future__ import annotations
import hashlib, json
from typing import Any

def _canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _canonical(value[k]) for k in sorted(value, key=lambda x: str(x))}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_canonical(item) for item in value), key=lambda x: json.dumps(x, sort_keys=True))
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"Unsupported SIF value type: {type(value).__name__}")

def fingerprint(observation: dict[str, Any]) -> str:
    """Hash canonical observations; callers must exclude secrets and personal identifiers."""
    encoded = json.dumps(_canonical(observation), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

def compare_fingerprints(baseline: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    """Return changed structural paths, never subtract digests."""
    changed: list[str] = []
    def walk(left: Any, right: Any, path: str) -> None:
        if isinstance(left, dict) and isinstance(right, dict):
            for key in sorted(set(left) | set(right), key=str):
                child = f"{path}.{key}" if path else str(key)
                if key not in left or key not in right: changed.append(child)
                else: walk(left[key], right[key], child)
        elif isinstance(left, list) and isinstance(right, list):
            if len(left) != len(right): changed.append(path or "$")
            else:
                for i, (a, b) in enumerate(zip(left, right)): walk(a, b, f"{path}[{i}]")
        elif left != right: changed.append(path or "$")
    walk(_canonical(baseline), _canonical(candidate), "")
    return changed
