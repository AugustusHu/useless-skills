#!/usr/bin/env python3
"""Render a normalized third-party API debug result as one self-contained HTML file."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SENSITIVE_KEY = re.compile(
    r"^(authorization|proxy[-_]?authorization|api[-_]?key|client[-_]?secret|"
    r"password|private[-_]?key|access[-_]?token|refresh[-_]?token|"
    r"webhook[-_]?secret|secret|signature|x[-_].*signature)$",
    re.IGNORECASE,
)
SAFE_REFERENCE = re.compile(r"^(ENV|FILE|KEYCHAIN):")
JWT = re.compile(r"(?<![A-Za-z0-9_-])eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")
SECRET_QUERY = re.compile(
    r"([?&](?:token|signature|api[-_]?key|secret)=)[^&\s]+", re.IGNORECASE
)


def redact(value: Any, key: str = "") -> Any:
    if SENSITIVE_KEY.search(key):
        if value is None:
            return None
        if isinstance(value, str) and (
            SAFE_REFERENCE.match(value) or value.startswith("[REDACTED")
        ):
            return value
        return "[REDACTED]"
    if isinstance(value, dict):
        return {k: redact(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return SECRET_QUERY.sub(r"\1[REDACTED]", JWT.sub("[REDACTED_JWT]", value))
    return value


def normalize(data: dict[str, Any]) -> dict[str, Any]:
    data.setdefault("meta", {})
    data.setdefault("input", {})
    data.setdefault("terminology", {})
    data.setdefault("regionSupport", {})
    for key in ("interfaces", "scenarios", "findings", "questions", "limitations", "sideEffects"):
        data.setdefault(key, [])
    data["meta"].setdefault("provider", "Third party")
    data["meta"].setdefault("status", "INCOMPLETE")
    data["meta"].setdefault("summary", "")
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_json", type=Path)
    parser.add_argument("output_html", type=Path)
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "assets" / "report-template.html",
    )
    args = parser.parse_args()

    data = normalize(redact(json.loads(args.run_json.read_text(encoding="utf-8"))))
    template = args.template.read_text(encoding="utf-8")
    title = f"{data['meta']['provider']} API Debug Report"
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )
    html = template.replace("__REPORT_TITLE__", title).replace("__REPORT_DATA__", payload)
    args.output_html.parent.mkdir(parents=True, exist_ok=True)
    args.output_html.write_text(html, encoding="utf-8")
    print(args.output_html.resolve())


if __name__ == "__main__":
    main()
