"""
A-CODE Lane — Edge-Matrix & Regression Suite (§26.2 TDD, §26.4 Naming, §26.6 Edge Matrix)
Run: python3 -m unittest discover -s demo/tests -p "test_*.py" -v
"""

import unittest
from demo.src.engine import MAX_PAYLOAD_CHARS, process_contract, process_unconstrained


class TestContractEngineEdgeMatrix(unittest.TestCase):
    def setUp(self) -> None:
        self.tenant = "acme-prod"
        self.seen: set[str] = set()

    def test_engine_approves_valid_happy_path_payload(self) -> None:
        res = process_contract(
            {
                "request_id": "req-001",
                "tenant": "acme-prod",
                "title": "Deploy auth token rotation v2",
                "severity": "S2",
            },
            current_tenant=self.tenant,
            seen_ids=self.seen,
        )
        self.assertTrue(res["ok"])
        self.assertEqual(res["code"], "OK_VERIFIED")
        self.assertIn("req-001", self.seen)

    def test_engine_rejects_null_or_non_dict_payload(self) -> None:
        res = process_contract(None, current_tenant=self.tenant, seen_ids=self.seen)
        self.assertFalse(res["ok"])
        self.assertEqual(res["code"], "ERR_MALFORMED")

    def test_engine_rejects_empty_and_whitespace_only_title(self) -> None:
        res = process_contract(
            {"request_id": "req-002", "tenant": "acme-prod", "title": "   \t\n  "},
            current_tenant=self.tenant,
            seen_ids=self.seen,
        )
        self.assertFalse(res["ok"])
        self.assertEqual(res["code"], "ERR_EMPTY_TITLE")

    def test_engine_normalizes_unicode_cjk_rtl_and_combining_marks(self) -> None:
        # 'e' + combining acute accent (\u0301) -> NFC 'é' (\u00e9) + CJK + Arabic RTL
        raw_title = "Cafe\u0301 東京リリース \u202eمرحبا"
        res = process_contract(
            {"request_id": "req-003", "tenant": "acme-prod", "title": raw_title},
            current_tenant=self.tenant,
            seen_ids=self.seen,
        )
        self.assertTrue(res["ok"])
        self.assertIn("Café", res["normalized_title"])
        self.assertIn("東京リリース", res["normalized_title"])

    def test_engine_rejects_10x_oversized_payload(self) -> None:
        oversized = "A" * (MAX_PAYLOAD_CHARS * 10)
        res = process_contract(
            {"request_id": "req-004", "tenant": "acme-prod", "title": oversized},
            current_tenant=self.tenant,
            seen_ids=self.seen,
        )
        self.assertFalse(res["ok"])
        self.assertEqual(res["code"], "ERR_PAYLOAD_TOO_LARGE")

    def test_engine_blocks_duplicate_retry_idempotently(self) -> None:
        payload = {"request_id": "req-dup", "tenant": "acme-prod", "title": "Cut release 1.4"}
        first = process_contract(payload, current_tenant=self.tenant, seen_ids=self.seen)
        second = process_contract(payload, current_tenant=self.tenant, seen_ids=self.seen)
        self.assertTrue(first["ok"])
        self.assertFalse(second["ok"])
        self.assertEqual(second["code"], "ERR_DUPLICATE_RETRY")
        self.assertEqual(second["status"], "SKIPPED_IDEMPOTENT")

    def test_engine_blocks_unauthorized_missing_tenant(self) -> None:
        res = process_contract(
            {"request_id": "req-005", "tenant": "", "title": "Hotfix"},
            current_tenant=self.tenant,
            seen_ids=self.seen,
        )
        self.assertFalse(res["ok"])
        self.assertEqual(res["code"], "ERR_UNAUTHORIZED")

    def test_engine_blocks_wrong_tenant_cross_tenant_write(self) -> None:
        res = process_contract(
            {"request_id": "req-006", "tenant": "other-corp", "title": "Steal release gate"},
            current_tenant=self.tenant,
            seen_ids=self.seen,
        )
        self.assertFalse(res["ok"])
        self.assertEqual(res["code"], "ERR_WRONG_TENANT")

    def test_engine_rejects_invalid_severity_enum(self) -> None:
        res = process_contract(
            {"request_id": "req-007", "tenant": "acme-prod", "title": "Valid", "severity": "P0-INVALID"},
            current_tenant=self.tenant,
            seen_ids=self.seen,
        )
        self.assertFalse(res["ok"])
        self.assertEqual(res["code"], "ERR_INVALID_SEVERITY")

    def test_unconstrained_baseline_demonstrates_known_failures(self) -> None:
        # Proves why the unconstrained baseline fails §26.6 & §28.2:
        # 1. Accepts whitespace-only title and wrong tenant without error
        bad = process_unconstrained({"title": "   ", "tenant": "wrong-tenant"})
        self.assertTrue(bad["ok"])
        self.assertEqual(bad["title"], "")
        self.assertIn("/Users/internal", bad["debug_path"])
        # 2. Crashes with KeyError on missing title
        with self.assertRaises(KeyError):
            process_unconstrained({})


if __name__ == "__main__":
    unittest.main()
