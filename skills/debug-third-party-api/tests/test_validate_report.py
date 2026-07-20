#!/usr/bin/env python3

import copy
import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_report.py"
TEMPLATE = Path(__file__).parents[1] / "assets" / "report-template.html"
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
    def test_side_effects_support_resource_ids_contract(self) -> None:
        template = TEMPLATE.read_text()
        self.assertIn("item.resourceIds?.length", template)
        self.assertIn("item.summary", template)
        self.assertNotIn(
            "`${item.class} × ${item.count}：${item.detail || \"\"}`",
            template,
        )

    def test_raw_messages_have_copy_control(self) -> None:
        template = TEMPLATE.read_text()
        self.assertIn('$("button", "copy-raw-button")', template)
        self.assertIn("navigator.clipboard?.writeText", template)
        self.assertIn('button.classList.add("copied")', template)

    def test_field_constraints_stay_in_existing_table_cell(self) -> None:
        template = TEMPLATE.read_text()
        self.assertIn("row.constraintEvidence", template)
        self.assertIn('kind === "response" ? "action" : "source"', template)
        self.assertIn('dataTable(item.requestFields, "request")', template)
        self.assertIn('dataTable(item.responseFields, "response")', template)
        self.assertNotIn("constraint-report", template)

    def test_client_id_is_treated_as_credential_data(self) -> None:
        data = report_data()
        data["input"]["environment"]["clientId"] = "visible-client-id"
        errors = validate_report.validate_data(data)
        self.assertIn(
            "sensitive value is not redacted: input.environment.clientId",
            errors,
        )

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
                "type": "integer",
                "required": True,
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

    def test_rejects_material_field_without_classification(self) -> None:
        data = report_data()
        data["interfaces"][0]["requestFields"] = [
            {
                "field": "customerReference",
                "type": "string",
                "required": True,
                "source": "Caller",
                "criticalFieldCategory": None,
                "documented": "Client reference",
                "documentSource": ["https://docs.example.test/reference"],
                "observed": "Not executed",
                "verdict": "NOT_EXECUTED",
                "evidenceIds": [],
            }
        ]
        errors = validate_report.validate_data(data)
        self.assertIn(
            "interfaces[0].requestFields[0].criticalFieldCategory cannot be null; "
            "field name indicates IDENTIFIER",
            errors,
        )

    def test_material_field_requires_dimension_evidence(self) -> None:
        data = report_data()
        data["interfaces"][0]["requestFields"] = [
            {
                "field": "amount",
                "type": "integer",
                "required": True,
                "source": "Caller",
                "criticalFieldCategory": "AMOUNT",
                "probeDimensions": [],
                "constraintEvidence": {},
                "documented": "Integer minor units",
                "documentSource": ["https://docs.example.test/amount"],
                "observed": "Not executed",
                "verdict": "NOT_EXECUTED",
                "evidenceIds": [],
            }
        ]
        errors = validate_report.validate_data(data)
        self.assertTrue(
            any("constraintEvidence missing dimensions" in error for error in errors),
            errors,
        )

    def test_accepts_explicit_unexecuted_constraint_evidence(self) -> None:
        data = report_data()
        constraint_evidence = {
            dimension: {
                "documented": "Official documentation is silent.",
                "observed": "Not executed because no valid field baseline was available.",
                "verdict": "NOT_EXECUTED",
                "evidenceIds": [],
            }
            for dimension in validate_report.REQUIRED_CONSTRAINT_DIMENSIONS["AMOUNT"]
        }
        data["interfaces"][0]["requestFields"] = [
            {
                "field": "amount",
                "type": "integer",
                "required": True,
                "source": "Caller",
                "criticalFieldCategory": "AMOUNT",
                "probeDimensions": [],
                "constraintEvidence": constraint_evidence,
                "documented": "Official documentation is silent.",
                "documentSource": ["https://docs.example.test/amount"],
                "observed": "No amount probe was executable.",
                "verdict": "NOT_EXECUTED",
                "evidenceIds": [],
            }
        ]
        self.assertEqual(validate_report.validate_data(data), [])

    def test_executed_constraint_dimension_requires_evidence(self) -> None:
        errors = []
        validate_report.validate_constraint_evidence(
            {
                "probeDimensions": ["format"],
                "constraintEvidence": {
                    dimension: {
                        "documented": "Declared",
                        "observed": "Observed",
                        "verdict": "NOT_EXECUTED",
                        "evidenceIds": [],
                    }
                    for dimension in validate_report.REQUIRED_CONSTRAINT_DIMENSIONS[
                        "PHONE"
                    ]
                },
            },
            "field",
            "PHONE",
            errors,
        )
        self.assertIn(
            "field.probeDimensions includes unexecuted dimension: format",
            errors,
        )

    def test_request_source_and_response_action_are_required(self) -> None:
        data = report_data()
        data["interfaces"][0]["requestFields"] = [
            {
                "field": "memo",
                "type": "string",
                "required": False,
                "criticalFieldCategory": None,
                "documented": "Optional memo",
                "documentSource": ["https://docs.example.test/memo"],
                "observed": "Not executed",
                "verdict": "NOT_EXECUTED",
            }
        ]
        data["interfaces"][0]["responseFields"] = [
            {
                "field": "result",
                "type": "string",
                "required": True,
                "documented": "Result value",
                "documentSource": ["https://docs.example.test/result"],
                "observed": "Returned",
                "verdict": "PASS",
                "evidenceIds": ["E-SUCCESS-01"],
            }
        ]
        errors = validate_report.validate_data(data)
        self.assertIn("interfaces[0].requestFields[0].source is required", errors)
        self.assertIn("interfaces[0].responseFields[0].action is required", errors)


if __name__ == "__main__":
    unittest.main()
