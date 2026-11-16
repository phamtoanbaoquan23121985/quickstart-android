"""TDD contract tests for AEGIS-Ω PHANTOM BOUNDARY.

These are pure-logic tests. They are not physical-device evidence.
"""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sif import fingerprint, compare_fingerprints
from bcl import Authority, AuthorityEdge, validate_authority_flow
from cbr import Experiment, build_one_factor_replays, compare_outcomes
from reality_gate import Evidence, FindingStatus, evaluate_reality_gate


class SIFTests(unittest.TestCase):
    def test_fingerprint_is_order_independent_for_mapping_keys(self):
        a = fingerprint({"identity": {"uid": 10, "pid": 2}, "outcome": "DENIED"})
        b = fingerprint({"outcome": "DENIED", "identity": {"pid": 2, "uid": 10}})
        self.assertEqual(a, b)

    def test_fingerprint_changes_when_security_relevant_value_changes(self):
        a = fingerprint({"permission": "DENIED"})
        b = fingerprint({"permission": "GRANTED"})
        self.assertNotEqual(a, b)

    def test_compare_returns_structural_paths_not_hash_subtraction(self):
        delta = compare_fingerprints(
            {"caller": {"uid": 10}, "decision": "DENIED"},
            {"caller": {"uid": 10}, "decision": "GRANTED"},
        )
        self.assertEqual(delta, ["decision"])


class BCLTests(unittest.TestCase):
    def test_authority_cannot_increase_without_explicit_delegation(self):
        source = Authority(level=1, capabilities=frozenset({"read"}))
        target = Authority(level=2, capabilities=frozenset({"read", "write"}))
        edge = AuthorityEdge(source, target, delegated_capabilities=frozenset())
        result = validate_authority_flow([edge])
        self.assertFalse(result.allowed)
        self.assertIn("write", result.unauthorized_capabilities)

    def test_explicit_scoped_delegation_allows_only_delegated_capability(self):
        source = Authority(level=1, capabilities=frozenset({"read"}))
        target = Authority(level=2, capabilities=frozenset({"read", "uri:content://demo/item"}))
        edge = AuthorityEdge(
            source, target,
            delegated_capabilities=frozenset({"uri:content://demo/item"}),
            delegation_evidence="test-grant-001",
        )
        self.assertTrue(validate_authority_flow([edge]).allowed)

    def test_delegation_without_evidence_is_rejected(self):
        source = Authority(level=1, capabilities=frozenset({"read"}))
        target = Authority(level=2, capabilities=frozenset({"read", "write"}))
        edge = AuthorityEdge(source, target, delegated_capabilities=frozenset({"write"}))
        self.assertFalse(validate_authority_flow([edge]).allowed)


class CBRTests(unittest.TestCase):
    def test_one_factor_replay_changes_one_dimension_at_a_time(self):
        baseline = Experiment(identity="authorized", authority="granted", payload="normal")
        replays = build_one_factor_replays(baseline, {
            "identity": ["unauthorized"],
            "authority": ["denied"],
            "payload": ["boundary"],
        })
        self.assertEqual(len(replays), 3)
        for replay in replays:
            changed = sum(getattr(replay, field) != getattr(baseline, field)
                          for field in ("identity", "authority", "payload"))
            self.assertEqual(changed, 1)

    def test_outcome_comparison_identifies_changed_fields(self):
        self.assertEqual(
            compare_outcomes({"decision": "DENIED", "side_effect": False},
                             {"decision": "GRANTED", "side_effect": False}),
            ["decision"],
        )


class RealityGateTests(unittest.TestCase):
    def test_inferred_or_synthetic_observation_never_becomes_validated(self):
        evidence = Evidence(
            device_codename="blazer", api_level=36, physical_device=True,
            scope_authorized=True, repeatable=True, invariant_violated=True,
            platform_attribution=True, safe_poc=True, independent_review=True,
            evidence_class="INFERRED",
        )
        result = evaluate_reality_gate(evidence)
        self.assertEqual(result.status, FindingStatus.CANDIDATE)
        self.assertFalse(result.reportable)

    def test_all_required_real_device_evidence_is_reportable_not_auto_confirmed(self):
        evidence = Evidence(
            device_codename="mustang", api_level=36, physical_device=True,
            scope_authorized=True, repeatable=True, invariant_violated=True,
            platform_attribution=True, safe_poc=True, independent_review=True,
            evidence_class="OBSERVED",
        )
        result = evaluate_reality_gate(evidence)
        self.assertEqual(result.status, FindingStatus.REPORTABLE)
        self.assertTrue(result.reportable)
        self.assertFalse(result.confirmed_vulnerability)

    def test_wrong_device_or_missing_scope_fails_closed(self):
        evidence = Evidence(
            device_codename="generic", api_level=36, physical_device=True,
            scope_authorized=False, repeatable=True, invariant_violated=True,
            platform_attribution=True, safe_poc=True, independent_review=True,
            evidence_class="OBSERVED",
        )
        result = evaluate_reality_gate(evidence)
        self.assertEqual(result.status, FindingStatus.REJECTED)
        self.assertFalse(result.reportable)

    def test_unrepeatable_result_remains_candidate(self):
        evidence = Evidence(
            device_codename="blazer", api_level=36, physical_device=True,
            scope_authorized=True, repeatable=False, invariant_violated=True,
            platform_attribution=True, safe_poc=True, independent_review=True,
            evidence_class="OBSERVED",
        )
        self.assertEqual(evaluate_reality_gate(evidence).status, FindingStatus.CANDIDATE)


if __name__ == "__main__":
    unittest.main()
