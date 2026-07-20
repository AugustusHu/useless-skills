#!/usr/bin/env python3

import copy
import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_report.py"
SPEC = importlib.util.spec_from_file_location("validate_report", SCRIPT)
validate_report = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(validate_report)


def case(case_id: str, outcome: str, status: int) -> dict:
    return {
        "id": case_id,
        "name": case_id,
        "probeOutcome": outcome,
        "verdict": "PASS",
        "request": {"method": "POST", "url": "https://sandbox.example.test/items"},
        "response": {"httpStatus": status, "body": {}},
        "evidenceIds": [f"E-{case_id}"],
    }


def report_data() -> dict:
    return {
        "meta": {"provider": "Example"},
        "input": {
            "documentation": [{"url": "https://docs.example.test"}],
            "environment": {},
            "interfaceScope": [{"requestedName": "Create item"}],
            "requestedScenarios": [],
        },
        "interfaces": [
            {
                "id": "create-item",
                "name": "Create item",
                "method": "POST",
                "url": "https://sandbox.example.test/items",
                "authentication": {},
                "signing": {},
                "encryption": {},
                "supportScope": {
                    "verdict": "PASS",
                    "official": {
                        "catalogMode": "INLINE",
                        "regions": ["NG"],
                        "currencies": ["NGN"],
                        "sourceRefs": ["https://docs.example.test/scope"],
                    },
                    "observed": {"regions": ["NG"], "currencies": ["NGN"]},
                    "evidenceIds": ["E-SCOPE-01"],
                },
                "requestFields": [],
                "responseFields": [],
                "errorCodes": [],
                "cases": [
                    case("SUCCESS-01", "SUCCESS", 200),
                    case("FAILURE-01", "FAILURE", 400),
                ],
            }
        ],
        "scenarios": [],
        "questions": [],
        "findings": [],
    }


class ProbeCoverageTest(unittest.TestCase):
    def test_accepts_success_and_failure_probe(self) -> None:
        self.assertEqual(validate_report.validate_data(report_data()), [])

    def test_rejects_missing_failure_probe(self) -> None:
        data = report_data()
        data["interfaces"][0]["cases"].pop()
        errors = validate_report.validate_data(data)
        self.assertIn(
            "interfaces[0] missing executed probe outcomes: FAILURE",
            errors,
        )

    def test_rejects_unexecuted_case_as_probe(self) -> None:
        data = copy.deepcopy(report_data())
        data["interfaces"][0]["cases"][1]["verdict"] = "BLOCKED"
        errors = validate_report.validate_data(data)
        self.assertTrue(
            any("must be an executed probe" in error for error in errors),
            errors,
        )
        self.assertIn(
            "interfaces[0] missing executed probe outcomes: FAILURE",
            errors,
        )

    def test_html_requires_probe_outcome_labels(self) -> None:
        html = " ".join(
            [
                'id="report-data"',
                'id="tabs"',
                'id="panels"',
                'id="interface-search"',
                "文档声明",
                "实测结果",
                "接入修订",
                "仅修订",
                "完整脱敏 Request",
                "完整脱敏 Response",
                "成功探测",
                "失败探测",
                "官方获取方式",
                "可执行代码示例",
                "Create item",
            ]
        )
        self.assertEqual(
            validate_report.validate_html(html, report_data()),
            [],
        )

    def test_contract_row_requires_official_source(self) -> None:
        errors = []
        validate_report.validate_contract_row(
            {
                "field": "amount",
                "documented": "Integer minor units",
                "verdict": "NOT_EXECUTED",
            },
            "field",
            "field",
            errors,
        )
        self.assertIn(
            "field.documentSource must contain at least one source reference",
            errors,
        )

    def test_dynamic_scope_requires_retrieval_instructions(self) -> None:
        data = report_data()
        scope = data["interfaces"][0]["supportScope"]
        scope["official"]["catalogMode"] = "RETRIEVAL"
        errors = validate_report.validate_data(data)
        self.assertIn(
            "interfaces[0].supportScope.retrieval is required for a dynamic catalog",
            errors,
        )

    def test_crypto_requires_source_and_code_example(self) -> None:
        errors = []
        validate_report.validate_crypto_dimension(
            {
                "official": {"algorithm": "HMAC-SHA512"},
                "localVerification": {
                    "verdict": "BLOCKED",
                    "observed": "Missing official encoding",
                    "evidenceIds": [],
                },
                "interoperability": {
                    "verdict": "BLOCKED",
                    "observed": "No callback captured",
                    "evidenceIds": [],
                },
            },
            "signing",
            "signing",
            errors,
        )
        self.assertIn(
            "signing.official.sourceRefs must contain at least one source reference",
            errors,
        )
        self.assertIn(
            "signing.localVerification.code is required as a reusable example",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
