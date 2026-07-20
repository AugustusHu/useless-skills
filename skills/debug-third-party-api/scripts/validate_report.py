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
PROBE_OUTCOMES = {"SUCCESS", "FAILURE"}
EXECUTED_VERDICTS = {"PASS", "DOCUMENT_MISMATCH", "OBSERVED"}
MATERIAL_FIELD_CATEGORIES = {
    "AMOUNT",
    "PHONE",
    "ACCOUNT_NUMBER",
    "ACCOUNT_NAME",
    "CARD",
    "IDENTITY",
    "INSTITUTION",
    "IDENTIFIER",
    "ENUM_ROUTING",
    "DATETIME",
    "TEXT",
    "CALLBACK_SECURITY",
}
REQUIRED_CONSTRAINT_DIMENSIONS = {
    "AMOUNT": {
        "currency", "unit", "precision", "rounding", "minimum", "maximum",
        "boundary", "format", "aggregateLimits",
    },
    "PHONE": {
        "format", "countryCode", "length", "charset", "supportedCountries",
        "normalization",
    },
    "ACCOUNT_NUMBER": {
        "format", "length", "charset", "checksum", "leadingZero", "separators",
        "maskingEncryption",
    },
    "ACCOUNT_NAME": {
        "format", "minimumLength", "maximumLength", "charset", "punctuation",
        "whitespace", "unicode", "matching", "masking",
    },
    "CARD": {
        "format", "length", "charset", "validation", "tokenExpiry",
        "storageLogging",
    },
    "IDENTITY": {
        "format", "length", "charset", "typeDependency", "dateSemantics",
        "maskingEncryption",
    },
    "INSTITUTION": {
        "format", "length", "providerMapping", "sourceBinding", "supportScope",
    },
    "IDENTIFIER": {
        "format", "length", "charset", "sourceGeneration", "uniqueness",
        "duplicateBehavior", "reconciliation",
    },
    "ENUM_ROUTING": {
        "values", "supportScope", "routingParty", "mapping", "routingBehavior",
        "unknownFallback",
    },
    "DATETIME": {
        "format", "timezone", "valueType", "timestampUnit", "precision",
        "expiryTimeout",
    },
    "TEXT": {
        "length", "charset", "specialCharacters", "unicode", "newlines",
        "escaping",
    },
    "CALLBACK_SECURITY": {
        "format", "https", "domainPolicy", "length", "encoding", "algorithm",
        "canonicalization", "failureHandling",
    },
}
MATERIAL_FIELD_NAMES = (
    ("AMOUNT", re.compile(r"(?:amount|balance)$")),
    ("PHONE", re.compile(r"(?:phone|phoneno|mobile|mobileno|msisdn|telephone)$")),
    ("ACCOUNT_NAME", re.compile(r"(?:accountname|walletname|payeename|beneficiaryname)$")),
    ("ACCOUNT_NUMBER", re.compile(r"(?:accountno|accountnumber|walletno|walletnumber|iban)$")),
    ("CARD", re.compile(r"(?:cardno|cardnumber|pan|expirydate|cvv|cvc|cardtoken|cardbin)$")),
    ("IDENTITY", re.compile(r"(?:idtype|idno|identitynumber|nin|bvn|dateofbirth|dob)$")),
    ("INSTITUTION", re.compile(r"(?:bankcode|swiftcode|bic|merchantid|institutioncode|institutionid)$")),
    ("IDENTIFIER", re.compile(r"(?:requestreference|customerreference|orderid|transactionid|channelorderid|channelresponseid|idempotencykey)$")),
    ("ENUM_ROUTING", re.compile(r"(?:currency|currencycode|country|countrycode|party|businesstype|ability|action|status)$")),
    ("DATETIME", re.compile(r"(?:timestamp|transactiontime|expirytime|createdat|updatedat|requestedat|datetime)$")),
    ("TEXT", re.compile(r"(?:narration|remark|description|smscontent)$")),
    ("CALLBACK_SECURITY", re.compile(r"(?:callbackurl|returnurl|webhookurl|signature|sign)$")),
)
CATALOG_MODES = {"INLINE", "RETRIEVAL"}
INTERFACE_KEYS = {
    "id",
    "name",
    "method",
    "url",
    "authentication",
    "signing",
    "encryption",
    "institutionSupport",
    "requestFields",
    "responseFields",
    "errorCodes",
    "cases",
}
SENSITIVE_KEY = re.compile(
    r"^(authorization|proxy[-_]?authorization|api[-_]?key|client[-_]?id|client[-_]?secret|"
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


def validate_source_refs(value: Any, path: str, errors: list[str]) -> None:
    refs = [value] if isinstance(value, str) else value
    if (
        not isinstance(refs, list)
        or not refs
        or any(not isinstance(item, str) or not item.strip() for item in refs)
    ):
        errors.append(f"{path} must contain at least one source reference")


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
    else:
        validate_source_refs(
            official.get("sourceRefs") or official.get("source"),
            f"{path}.official.sourceRefs",
            errors,
        )
        if dimension == "signing" and not official.get("algorithm"):
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
        executed = verdict in EXECUTED_VERDICTS
        if executed and not section.get("evidenceIds"):
            errors.append(f"{section_path}.evidenceIds is required for executed claims")
        if section_name == "localVerification" and not section.get("code"):
            errors.append(f"{section_path}.code is required as a reusable example")


def validate_region_support(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return
    if not isinstance(value.get("summary"), str) or not value["summary"].strip():
        errors.append(f"{path}.summary is required")
    validate_source_refs(value.get("sourceRefs"), f"{path}.sourceRefs", errors)


def validate_institution_support(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return
    verdict = value.get("verdict")
    if verdict not in VERDICTS:
        errors.append(f"{path}.verdict is invalid")
    if verdict == "NOT_APPLICABLE":
        if not value.get("detail"):
            errors.append(f"{path}.detail is required when not applicable")
        return
    official = value.get("official")
    if not isinstance(official, dict) or not official:
        errors.append(f"{path}.official must contain documented institution support")
        return
    for section_name in ("official", "observed"):
        section = value.get(section_name)
        if not isinstance(section, dict):
            continue
        forbidden = sorted({"regions", "countries", "currencies"} & set(section))
        if forbidden:
            errors.append(
                f"{path}.{section_name} must not contain system regions or currencies: "
                f"{', '.join(forbidden)}"
            )
    mode = official.get("catalogMode")
    if mode not in CATALOG_MODES:
        errors.append(f"{path}.official.catalogMode must be INLINE or RETRIEVAL")
    validate_source_refs(
        official.get("sourceRefs"),
        f"{path}.official.sourceRefs",
        errors,
    )
    scope_values = {
        key: item
        for key, item in official.items()
        if key not in {"catalogMode", "sourceRefs"} and item not in (None, "", [], {})
    }
    if not scope_values:
        errors.append(f"{path}.official must describe institution support")
    observed = value.get("observed")
    if not isinstance(observed, dict) or not observed:
        errors.append(f"{path}.observed must contain runtime observations")
    if verdict in EXECUTED_VERDICTS and not value.get("evidenceIds"):
        errors.append(f"{path}.evidenceIds is required for executed observations")
    if mode == "RETRIEVAL":
        retrieval = value.get("retrieval")
        if not isinstance(retrieval, dict) or not retrieval:
            errors.append(f"{path}.retrieval is required for a dynamic catalog")
        else:
            if not retrieval.get("instructions"):
                errors.append(f"{path}.retrieval.instructions is required")
            if not any(
                retrieval.get(key)
                for key in ("url", "interfaceId", "documentation")
            ):
                errors.append(
                    f"{path}.retrieval requires url, interfaceId, or documentation"
                )


def validate_contract_row(
    row: Any, path: str, identity_key: str, errors: list[str]
) -> None:
    if not isinstance(row, dict):
        errors.append(f"{path} must be an object")
        return
    if not row.get(identity_key):
        errors.append(f"{path}.{identity_key} is required")
    if identity_key == "field":
        if row.get("type") in (None, "", [], {}):
            errors.append(f"{path}.type is required")
        if "required" not in row or row.get("required") in (None, ""):
            errors.append(f"{path}.required is required")
    if row.get("documented") in (None, "", [], {}):
        errors.append(f"{path}.documented is required")
    validate_source_refs(row.get("documentSource"), f"{path}.documentSource", errors)
    verdict = row.get("verdict")
    if verdict not in VERDICTS:
        errors.append(f"{path}.verdict is invalid")
        return
    executed = verdict in EXECUTED_VERDICTS
    if executed and not row.get("evidenceIds"):
        errors.append(f"{path}.evidenceIds is required for executed claims")
    if verdict == "DOCUMENT_MISMATCH" and not row.get("correction"):
        errors.append(f"{path}.correction is required for a document mismatch")


def inferred_material_category(field_name: Any) -> str | None:
    if not isinstance(field_name, str):
        return None
    normalized = re.sub(r"[^a-z0-9]", "", field_name.lower())
    for category, pattern in MATERIAL_FIELD_NAMES:
        if pattern.search(normalized):
            return category
    return None


def validate_constraint_evidence(
    field: dict[str, Any], path: str, category: str, errors: list[str]
) -> None:
    evidence = field.get("constraintEvidence")
    if not isinstance(evidence, dict):
        errors.append(f"{path}.constraintEvidence must be an object")
        return
    required_dimensions = REQUIRED_CONSTRAINT_DIMENSIONS[category]
    missing = sorted(required_dimensions - set(evidence))
    if missing:
        errors.append(
            f"{path}.constraintEvidence missing dimensions: {', '.join(missing)}"
        )
    for dimension, claim in evidence.items():
        claim_path = f"{path}.constraintEvidence.{dimension}"
        if not isinstance(claim, dict):
            errors.append(f"{claim_path} must be an object")
            continue
        if claim.get("documented") in (None, "", [], {}):
            errors.append(f"{claim_path}.documented is required")
        if claim.get("observed") in (None, "", [], {}):
            errors.append(f"{claim_path}.observed is required")
        verdict = claim.get("verdict")
        if verdict not in VERDICTS:
            errors.append(f"{claim_path}.verdict is invalid")
        elif verdict in EXECUTED_VERDICTS and not claim.get("evidenceIds"):
            errors.append(f"{claim_path}.evidenceIds is required for executed claims")
        elif verdict in {"BLOCKED", "NOT_EXECUTED"}:
            reason = str(claim.get("observed", "")).strip().lower()
            if reason in {"blocked", "not executed", "阻塞", "未执行"}:
                errors.append(f"{claim_path}.observed requires a concrete reason")
    probe_dimensions = field.get("probeDimensions")
    if not isinstance(probe_dimensions, list):
        errors.append(f"{path}.probeDimensions must be a list")
        return
    for dimension in probe_dimensions:
        if dimension not in evidence:
            errors.append(
                f"{path}.probeDimensions references missing constraint evidence: "
                f"{dimension}"
            )
            continue
        if evidence[dimension].get("verdict") not in EXECUTED_VERDICTS:
            errors.append(
                f"{path}.probeDimensions includes unexecuted dimension: {dimension}"
            )


def validate_data(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    meta = data.get("meta", {})
    input_data = data.get("input", {})
    if not meta.get("provider"):
        errors.append("meta.provider is required")
    validate_region_support(data.get("regionSupport"), "regionSupport", errors)
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
            validate_institution_support(
                interface.get("institutionSupport"),
                f"interfaces[{index}].institutionSupport",
                errors,
            )
            validate_crypto_dimension(
                interface.get("encryption"),
                f"interfaces[{index}].encryption",
                "encryption",
                errors,
            )
            probe_outcomes: set[str] = set()
            cases = interface.get("cases", [])
            if not isinstance(cases, list):
                errors.append(f"interfaces[{index}].cases must be a list")
                cases = []
            for case_index, case in enumerate(cases):
                case_path = f"interfaces[{index}].cases[{case_index}]"
                if not isinstance(case, dict):
                    errors.append(f"{case_path} must be an object")
                    continue
                verdict = case.get("verdict")
                if verdict not in VERDICTS:
                    errors.append(
                        f"{case_path} has invalid verdict"
                    )
                elif verdict not in EXECUTED_VERDICTS:
                    errors.append(
                        f"{case_path} must be an executed probe; "
                        "blocked or unexecuted intentions do not belong in cases"
                    )
                elif not case.get("evidenceIds"):
                    errors.append(f"{case_path}.evidenceIds is required")
                outcome = case.get("probeOutcome")
                if outcome not in PROBE_OUTCOMES:
                    errors.append(
                        f"{case_path}.probeOutcome must be SUCCESS or FAILURE"
                    )
                elif verdict in EXECUTED_VERDICTS:
                    probe_outcomes.add(outcome)
                for message_name in ("request", "response"):
                    message = case.get(message_name)
                    if not isinstance(message, dict) or not message:
                        errors.append(f"{case_path}.{message_name} is required")
            missing_outcomes = sorted(PROBE_OUTCOMES - probe_outcomes)
            if missing_outcomes:
                errors.append(
                    f"interfaces[{index}] missing executed probe outcomes: "
                    f"{', '.join(missing_outcomes)}"
                )
            for field_group in ("requestFields", "responseFields"):
                for field_index, field in enumerate(interface.get(field_group, [])):
                    field_path = (
                        f"interfaces[{index}].{field_group}[{field_index}]"
                    )
                    validate_contract_row(
                        field,
                        field_path,
                        "field",
                        errors,
                    )
                    role_key = "source" if field_group == "requestFields" else "action"
                    if field.get(role_key) in (None, "", [], {}):
                        errors.append(f"{field_path}.{role_key} is required")
            for error_index, error_code in enumerate(interface.get("errorCodes", [])):
                validate_contract_row(
                    error_code,
                    f"interfaces[{index}].errorCodes[{error_index}]",
                    "code",
                    errors,
                )
            for field_index, field in enumerate(interface.get("requestFields", [])):
                field_path = f"interfaces[{index}].requestFields[{field_index}]"
                if "criticalFieldCategory" not in field:
                    errors.append(
                        f"{field_path}.criticalFieldCategory is required; use null "
                        "only after material-field review"
                    )
                    continue
                category = field.get("criticalFieldCategory")
                inferred_category = inferred_material_category(field.get("field"))
                if category is None:
                    if inferred_category:
                        errors.append(
                            f"{field_path}.criticalFieldCategory cannot be null; "
                            f"field name indicates {inferred_category}"
                        )
                    continue
                if category not in MATERIAL_FIELD_CATEGORIES:
                    errors.append(
                        f"{field_path} "
                        "has invalid criticalFieldCategory"
                    )
                    continue
                field_name = field.get("field")
                if not field_name:
                    errors.append(
                        f"{field_path}.field "
                        "is required for a critical field"
                    )
                validate_constraint_evidence(field, field_path, category, errors)
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
        "成功探测",
        "失败探测",
        "官方获取方式",
        "可执行代码示例",
        "全系统支持地域",
        "支持机构",
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
