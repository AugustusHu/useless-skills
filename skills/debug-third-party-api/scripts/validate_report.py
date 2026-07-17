#!/usr/bin/env python3
"""Validate normalized report data, required interface dimensions, and secret hygiene."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


VERDICTS = {
    "PASS",
    "DOCUMENT_MISMATCH",
    "OBSERVED",
    "BLOCKED",
    "NOT_APPLICABLE",
    "NOT_EXECUTED",
}
QUESTION_PRIORITIES = {"P0", "P1", "P2"}
FINANCIAL_FIELD_CATEGORIES = {
    "AMOUNT",
    "PHONE",
    "ACCOUNT_NUMBER",
    "ACCOUNT_NAME",
}
REQUIRED_PROBE_DIMENSIONS = {
    "AMOUNT": {"minimum", "maximum", "unit", "format"},
    "PHONE": {"format", "supportedCountries"},
    "ACCOUNT_NUMBER": {"format"},
    "ACCOUNT_NAME": {"format"},
}
INTERFACE_KEYS = {
    "id",
    "name",
    "method",
    "url",
    "authentication",
    "signing",
    "encryption",
    "supportScope",
    "requestFields",
    "responseFields",
    "errorCodes",
    "cases",
}
SENSITIVE_KEY = re.compile(
    r"^(authorization|proxy[-_]?authorization|api[-_]?key|client[-_]?secret|"
    r"password|private[-_]?key|access[-_]?token|refresh[-_]?token|"
    r"webhook[-_]?secret|secret|signature|x[-_].*signature)$",
    re.IGNORECASE,
)
SAFE_VALUE = re.compile(r"^(\[REDACTED.*\]|ENV:|FILE:|KEYCHAIN:)")
JWT = re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")
SECRET_QUERY = re.compile(
    r"[?&](?:token|signature|api[-_]?key|secret)=(?!\[REDACTED\])[^&\s]+",
    re.IGNORECASE,
)


def visit_sensitive(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            current = f"{path}.{key}" if path else key
            if SENSITIVE_KEY.search(key) and item not in (None, "", {}, []):
                if not isinstance(item, str) or not SAFE_VALUE.match(item):
                    errors.append(f"sensitive value is not redacted: {current}")
            visit_sensitive(item, current, errors)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            visit_sensitive(item, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        if JWT.search(value):
            errors.append(f"JWT-like value found: {path}")
        if SECRET_QUERY.search(value):
            errors.append(f"sensitive query value found: {path}")


def validate_crypto_dimension(
    value: Any, path: str, dimension: str, errors: list[str]
) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return
    if "official" not in value:
        return
    official = value.get("official")
    if not isinstance(official, dict) or not official:
        errors.append(f"{path}.official must contain the documented contract")
    elif dimension == "signing" and not official.get("algorithm"):
        errors.append(f"{path}.official.algorithm is required")
    elif dimension == "encryption" and not (
        official.get("algorithm") or official.get("transport")
    ):
        errors.append(f"{path}.official requires algorithm or transport")
    for section_name in ("localVerification", "interoperability"):
        section_path = f"{path}.{section_name}"
        section = value.get(section_name)
        if not isinstance(section, dict):
            errors.append(f"{section_path} is required")
            continue
        verdict = section.get("verdict")
        if verdict not in VERDICTS:
            errors.append(f"{section_path}.verdict is invalid")
        if not section.get("observed"):
            errors.append(f"{section_path}.observed is required")
        executed = verdict in {"PASS", "DOCUMENT_MISMATCH", "OBSERVED"}
        if executed and not section.get("evidenceIds"):
            errors.append(f"{section_path}.evidenceIds is required for executed claims")
        if section_name == "localVerification" and executed and not section.get("code"):
            errors.append(f"{section_path}.code is required for executed local checks")


def validate_contract_row(
    row: Any, path: str, identity_key: str, errors: list[str]
) -> None:
    if not isinstance(row, dict):
        errors.append(f"{path} must be an object")
        return
    if not row.get(identity_key):
        errors.append(f"{path}.{identity_key} is required")
    verdict = row.get("verdict")
    if verdict not in VERDICTS:
        errors.append(f"{path}.verdict is invalid")
        return
    executed = verdict in {"PASS", "DOCUMENT_MISMATCH", "OBSERVED"}
    if executed and not row.get("evidenceIds"):
        errors.append(f"{path}.evidenceIds is required for executed claims")
    if verdict == "DOCUMENT_MISMATCH" and not row.get("correction"):
        errors.append(f"{path}.correction is required for a document mismatch")


def validate_data(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    meta = data.get("meta", {})
    input_data = data.get("input", {})
    if not meta.get("provider"):
        errors.append("meta.provider is required")
    if not input_data.get("documentation"):
        errors.append("input.documentation is required")
    if "environment" not in input_data:
        errors.append("input.environment is required")
    if not input_data.get("interfaceScope"):
        errors.append("input.interfaceScope is required")
    interfaces = data.get("interfaces")
    if not isinstance(interfaces, list) or not interfaces:
        errors.append("interfaces must contain at least one interface")
    else:
        ids: set[str] = set()
        for index, interface in enumerate(interfaces):
            missing = sorted(INTERFACE_KEYS - set(interface))
            if missing:
                errors.append(f"interfaces[{index}] missing: {', '.join(missing)}")
            interface_id = interface.get("id")
            if interface_id in ids:
                errors.append(f"duplicate interface id: {interface_id}")
            ids.add(interface_id)
            validate_crypto_dimension(
                interface.get("signing"),
                f"interfaces[{index}].signing",
                "signing",
                errors,
            )
            validate_crypto_dimension(
                interface.get("encryption"),
                f"interfaces[{index}].encryption",
                "encryption",
                errors,
            )
            for case_index, case in enumerate(interface.get("cases", [])):
                if case.get("verdict") not in VERDICTS:
                    errors.append(
                        f"interfaces[{index}].cases[{case_index}] has invalid verdict"
                    )
            for field_group in ("requestFields", "responseFields"):
                for field_index, field in enumerate(interface.get(field_group, [])):
                    validate_contract_row(
                        field,
                        f"interfaces[{index}].{field_group}[{field_index}]",
                        "field",
                        errors,
                    )
            for error_index, error_code in enumerate(interface.get("errorCodes", [])):
                validate_contract_row(
                    error_code,
                    f"interfaces[{index}].errorCodes[{error_index}]",
                    "code",
                    errors,
                )
            for field_index, field in enumerate(interface.get("requestFields", [])):
                category = field.get("criticalFieldCategory")
                if category is None:
                    continue
                if category not in FINANCIAL_FIELD_CATEGORIES:
                    errors.append(
                        f"interfaces[{index}].requestFields[{field_index}] "
                        "has invalid criticalFieldCategory"
                    )
                field_name = field.get("field")
                if not field_name:
                    errors.append(
                        f"interfaces[{index}].requestFields[{field_index}].field "
                        "is required for a critical field"
                    )
                else:
                    dimensions = set(field.get("probeDimensions", []))
                    missing_dimensions = sorted(
                        REQUIRED_PROBE_DIMENSIONS.get(category, set()) - dimensions
                    )
                    if missing_dimensions:
                        errors.append(
                            f"interfaces[{index}].requestFields[{field_index}] "
                            "missing financial probe dimensions: "
                            f"{', '.join(missing_dimensions)}"
                        )
        scenarios = data.get("scenarios", [])
        for index, scenario in enumerate(scenarios):
            if scenario.get("verdict") not in VERDICTS:
                errors.append(f"scenarios[{index}] has invalid verdict")
            if scenario.get("origin") not in {"requested", "inferred"}:
                errors.append(f"scenarios[{index}] origin must be requested or inferred")
            if scenario.get("verdict") in {"BLOCKED", "NOT_EXECUTED"}:
                has_reason = bool(scenario.get("notes")) or any(
                    step.get("observed") for step in scenario.get("steps", [])
                )
                if not has_reason:
                    errors.append(
                        f"scenarios[{index}] {scenario.get('verdict')} requires a reason"
                    )
            for step_index, step in enumerate(scenario.get("steps", [])):
                step_path = f"scenarios[{index}].steps[{step_index}]"
                verdict = step.get("verdict")
                if verdict not in VERDICTS:
                    errors.append(f"{step_path}.verdict is invalid")
                if verdict in {"PASS", "DOCUMENT_MISMATCH", "OBSERVED"} and not step.get(
                    "evidenceIds"
                ):
                    errors.append(
                        f"{step_path}.evidenceIds is required for executed claims"
                    )

        requested = input_data.get("requestedScenarios", [])
        requested_records = [
            scenario for scenario in scenarios if scenario.get("origin") == "requested"
        ]
        if len(requested_records) != len(requested):
            errors.append(
                "requested scenario count mismatch: "
                f"input has {len(requested)}, report has {len(requested_records)}"
            )
        for item in requested:
            label = item if isinstance(item, str) else item.get("name")
            matches = [
                scenario
                for scenario in requested_records
                if scenario.get("requestedScenario") == label
            ]
            if len(matches) != 1:
                errors.append(
                    f"requested scenario must map exactly once: {label!r}"
                )
    for index, question in enumerate(data.get("questions", [])):
        if not isinstance(question, dict):
            errors.append(f"questions[{index}] must be a prioritized object")
            continue
        if question.get("priority") not in QUESTION_PRIORITIES:
            errors.append(f"questions[{index}] priority must be P0, P1, or P2")
        if not question.get("question"):
            errors.append(f"questions[{index}].question is required")
    for index, finding in enumerate(data.get("findings", [])):
        if finding.get("severity") not in QUESTION_PRIORITIES:
            errors.append(f"findings[{index}].severity must be P0, P1, or P2")
        if finding.get("category") not in VERDICTS:
            errors.append(f"findings[{index}].category is invalid")
        if finding.get("category") in {
            "PASS",
            "DOCUMENT_MISMATCH",
            "OBSERVED",
        } and not finding.get("evidenceIds"):
            errors.append(f"findings[{index}].evidenceIds is required")
    visit_sensitive(data, "", errors)
    return errors


def validate_html(html: str, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for marker in (
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
    ):
        if marker not in html:
            errors.append(f"HTML missing marker: {marker}")
    if "BEGIN PRIVATE KEY" in html or JWT.search(html) or SECRET_QUERY.search(html):
        errors.append("HTML contains a private key, JWT, or sensitive query value")
    for interface in data.get("interfaces", []):
        if interface.get("name") and interface["name"] not in html:
            errors.append(f"HTML missing interface name: {interface['name']}")
    has_crypto_evidence = any(
        isinstance(interface.get(dimension), dict)
        and "official" in interface[dimension]
        for interface in data.get("interfaces", [])
        for dimension in ("signing", "encryption")
    )
    if has_crypto_evidence:
        for marker in ("密码学实现与验证", "官方说明", "本地代码实测", "真实第三方互操作"):
            if marker not in html:
                errors.append(f"HTML missing cryptographic marker: {marker}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_json", type=Path)
    parser.add_argument("report_html", type=Path)
    args = parser.parse_args()

    data = json.loads(args.run_json.read_text(encoding="utf-8"))
    html = args.report_html.read_text(encoding="utf-8")
    errors = validate_data(data) + validate_html(html, data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    print("Report validation passed")


if __name__ == "__main__":
    main()
