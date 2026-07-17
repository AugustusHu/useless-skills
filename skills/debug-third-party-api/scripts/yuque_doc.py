#!/usr/bin/env python3
"""Read, pull, and update Yuque Markdown documents by their browser URL."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TOKEN_PLACEHOLDER = "PASTE_YOUR_YUQUE_TOKEN_HERE"
YUQUE_TOKEN = TOKEN_PLACEHOLDER
USER_AGENT = "debug-third-party-api-yuque/1.0"
TIMEOUT_SECONDS = 30


class YuqueError(RuntimeError):
    """Actionable Yuque client error."""


class YuqueHTTPError(YuqueError):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status


@dataclass(frozen=True)
class YuqueLocation:
    origin: str
    api_base: str
    namespace: str
    doc_slug: str
    source_url: str


def parse_yuque_url(value: str) -> YuqueLocation:
    parsed = urllib.parse.urlsplit(value.strip())
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https":
        raise YuqueError("Yuque URL must use HTTPS")
    if host != "yuque.com" and not host.endswith(".yuque.com"):
        raise YuqueError("Expected a yuque.com document URL")
    parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]
    if len(parts) < 3:
        raise YuqueError(
            "Expected Yuque URL path /<namespace>/<book>/<document-slug>"
        )
    origin = f"https://{parsed.netloc}"
    clean_path = "/" + "/".join(
        urllib.parse.quote(part, safe="-._~") for part in parts[:3]
    )
    return YuqueLocation(
        origin=origin,
        api_base=f"{origin}/api/v2",
        namespace=f"{parts[0]}/{parts[1]}",
        doc_slug=parts[2],
        source_url=f"{origin}{clean_path}",
    )


def resolve_token() -> str:
    token = os.environ.get("YUQUE_TOKEN", "").strip() or YUQUE_TOKEN.strip()
    if not token or token == TOKEN_PLACEHOLDER:
        raise YuqueError(
            "Yuque token is not configured. Set YUQUE_TOKEN or replace "
            "YUQUE_TOKEN in scripts/yuque_doc.py."
        )
    return token


def json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )


def unwrap_response(raw: bytes, url: str) -> Any:
    if not raw:
        return None
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise YuqueError(f"Yuque returned invalid JSON for {url}") from exc
    if isinstance(value, dict) and "data" in value:
        return value["data"]
    return value


class YuqueClient:
    def __init__(self, api_base: str, token: str) -> None:
        self.api_base = api_base.rstrip("/")
        self.token = token

    def request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.api_base}{path}"
        if query:
            url += "?" + urllib.parse.urlencode(query)
        data = json_bytes(payload) if payload is not None else None
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "X-Auth-Token": self.token,
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return unwrap_response(response.read(), url)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:600]
            raise YuqueHTTPError(
                exc.code,
                f"Yuque API {method} {url} returned HTTP {exc.code}: {detail}"
            ) from exc
        except urllib.error.URLError as exc:
            raise YuqueError(f"Yuque API request failed for {url}: {exc.reason}") from exc

    @staticmethod
    def repo_path(namespace: str) -> str:
        return urllib.parse.quote(namespace, safe="/-._~")

    def get_doc(self, location: YuqueLocation) -> dict[str, Any]:
        namespace = self.repo_path(location.namespace)
        slug = urllib.parse.quote(location.doc_slug, safe="-._~")
        value = self.request("GET", f"/repos/{namespace}/docs/{slug}")
        if not isinstance(value, dict) or not isinstance(value.get("id"), int):
            raise YuqueError("Yuque document response did not include a numeric id")
        return value

    def get_markdown(self, doc_id: int, fallback: str | None = None) -> tuple[str, str]:
        try:
            value = self.request("GET", "/yfm/docs", query={"doc_id": doc_id})
            if isinstance(value, dict) and isinstance(value.get("yfm"), str):
                return value["yfm"], "YMD"
        except YuqueHTTPError as exc:
            if exc.status not in {404, 410} or fallback is None:
                raise
        if fallback is None:
            raise YuqueError("Yuque YMD response did not include yfm content")
        return fallback, "LEGACY_BODY_FALLBACK"

    def list_docs(self, namespace: str) -> list[dict[str, Any]]:
        repo = self.repo_path(namespace)
        docs: list[dict[str, Any]] = []
        offset = 0
        while True:
            page = self.request(
                "GET",
                f"/repos/{repo}/docs",
                query={"offset": offset, "limit": 100},
            )
            if not isinstance(page, list):
                raise YuqueError("Yuque document-list response was not an array")
            docs.extend(item for item in page if isinstance(item, dict))
            if len(page) < 100:
                return docs
            offset += len(page)

    def update_markdown(self, doc_id: int, markdown: str) -> dict[str, Any]:
        value = self.request(
            "PUT",
            "/yfm/docs",
            payload={"doc_id": doc_id, "yfm": markdown},
        )
        if not isinstance(value, dict):
            raise YuqueError("Yuque update response was not an object")
        return value


def safe_filename(value: str, fallback: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return normalized or fallback


def compact_metadata(
    location: YuqueLocation,
    doc: dict[str, Any],
    *,
    read_mode: str | None = None,
    output: Path | None = None,
) -> dict[str, Any]:
    metadata = {
        "sourceUrl": location.source_url,
        "apiBase": location.api_base,
        "namespace": location.namespace,
        "docId": doc.get("id") or doc.get("doc_id"),
        "slug": doc.get("slug") or location.doc_slug,
        "title": doc.get("title"),
        "updatedAt": doc.get("updated_at"),
    }
    if read_mode:
        metadata["readMode"] = read_mode
    if output:
        metadata["output"] = str(output.resolve())
    return metadata


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def command_read(args: argparse.Namespace) -> None:
    location = parse_yuque_url(args.url)
    client = YuqueClient(location.api_base, resolve_token())
    doc = client.get_doc(location)
    markdown, read_mode = client.get_markdown(doc["id"], doc.get("body"))
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")
        metadata = compact_metadata(
            location, doc, read_mode=read_mode, output=output
        )
        if args.meta_output:
            write_json(Path(args.meta_output), metadata)
        print(json.dumps(metadata, ensure_ascii=False, indent=2))
        return
    sys.stdout.write(markdown)
    if markdown and not markdown.endswith("\n"):
        sys.stdout.write("\n")


def command_pull(args: argparse.Namespace) -> None:
    location = parse_yuque_url(args.url)
    client = YuqueClient(location.api_base, resolve_token())
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    for index, doc in enumerate(client.list_docs(location.namespace), start=1):
        doc_id = doc.get("id")
        if not isinstance(doc_id, int):
            raise YuqueError("Yuque document-list item did not include a numeric id")
        markdown, read_mode = client.get_markdown(doc_id, doc.get("body"))
        slug = str(doc.get("slug") or doc_id)
        filename = f"{index:03d}-{safe_filename(slug, str(doc_id))}.md"
        output = output_dir / filename
        output.write_text(markdown, encoding="utf-8")
        manifest.append(
            {
                "docId": doc_id,
                "title": doc.get("title"),
                "slug": doc.get("slug"),
                "updatedAt": doc.get("updated_at"),
                "readMode": read_mode,
                "file": filename,
            }
        )
    manifest_path = output_dir / "manifest.json"
    write_json(
        manifest_path,
        {
            "sourceUrl": location.source_url,
            "apiBase": location.api_base,
            "namespace": location.namespace,
            "documents": manifest,
        },
    )
    print(
        json.dumps(
            {
                "namespace": location.namespace,
                "documentCount": len(manifest),
                "outputDir": str(output_dir.resolve()),
                "manifest": str(manifest_path.resolve()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def command_update(args: argparse.Namespace) -> None:
    location = parse_yuque_url(args.url)
    input_path = Path(args.input)
    markdown = input_path.read_text(encoding="utf-8")
    client = YuqueClient(location.api_base, resolve_token())
    current = client.get_doc(location)
    result = client.update_markdown(current["id"], markdown)
    print(
        json.dumps(
            {
                "sourceUrl": location.source_url,
                "namespace": location.namespace,
                "docId": result.get("doc_id") or current["id"],
                "title": result.get("title") or current.get("title"),
                "updatedAt": result.get("updated_at"),
                "input": str(input_path.resolve()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read, pull, or update Yuque Markdown documents."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    read = subparsers.add_parser("read", help="Read one document as Markdown")
    read.add_argument("url", help="Yuque browser document URL")
    read.add_argument("--output", help="Write Markdown to this file")
    read.add_argument("--meta-output", help="Write compact metadata JSON")
    read.set_defaults(handler=command_read)

    pull = subparsers.add_parser("pull", help="Pull all documents in the target book")
    pull.add_argument("url", help="Any Yuque document URL in the target book")
    pull.add_argument("--output-dir", required=True, help="Destination directory")
    pull.set_defaults(handler=command_pull)

    update = subparsers.add_parser("update", help="Replace one document's Markdown body")
    update.add_argument("url", help="Yuque browser document URL")
    update.add_argument("--input", required=True, help="Markdown file to publish")
    update.set_defaults(handler=command_update)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        args.handler(args)
    except (YuqueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
