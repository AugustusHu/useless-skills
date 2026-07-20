# Evidence and report model

Store one JSON object. Empty dimensions must be explicit rather than omitted.

```json
{
  "meta": {
    "provider": "Provider canonical name",
    "channel": null,
    "environment": "Test",
    "generatedAt": "ISO-8601",
    "status": "COMPLETE_WITH_LIMITATIONS",
    "summary": "Concise observed outcome"
  },
  "input": {
    "documentation": [],
    "environment": {},
    "interfaceScope": [],
    "requestedScenarios": []
  },
  "terminology": {
    "provider": {"canonical": "Provider", "aliases": []},
    "businessTerms": {},
    "protocolLiterals": []
  },
  "interfaces": [
    {
      "id": "interface-1",
      "name": "Official interface name",
      "method": "POST",
      "url": "https://...",
      "description": "",
      "authentication": {},
      "signing": {},
      "encryption": {},
      "supportScope": {},
      "requestFields": [],
      "responseFields": [],
      "errorCodes": [],
      "cases": []
    }
  ],
  "scenarios": [],
  "findings": [],
  "questions": [],
  "limitations": [],
  "sideEffects": []
}
```

## Side effects

Record each externally visible test effect with the created resource IDs when available:

```json
{
  "class": "TEST_CREATE",
  "interfaceId": "create-resource",
  "summary": "Created sandbox resources.",
  "resourceIds": ["resource-1", "resource-2"]
}
```

The report derives the count from `resourceIds`. Use `count` only when exact IDs cannot be retained.

## Field rows

Use the same keys for request and response rows:

```json
{
  "field": "customerReference",
  "type": "string",
  "required": true,
  "source": "Caller-generated per request",
  "verdict": "PASS",
  "criticalFieldCategory": "IDENTIFIER",
  "probeDimensions": ["format", "uniqueness", "duplicateBehavior"],
  "constraintEvidence": {
    "format": {
      "documented": "Official documentation does not declare a format.",
      "observed": "已执行 ASCII 和 Unicode 探测。",
      "verdict": "OBSERVED",
      "evidenceIds": ["E-001", "E-002"]
    },
    "length": {
      "documented": "Official documentation does not declare a length.",
      "observed": "未执行：可接受的最大长度仍未知。",
      "verdict": "NOT_EXECUTED",
      "evidenceIds": []
    },
    "charset": {
      "documented": "Official documentation does not declare a character set.",
      "observed": "已执行 ASCII 和 Unicode 探测。",
      "verdict": "OBSERVED",
      "evidenceIds": ["E-001", "E-002"]
    },
    "sourceGeneration": {
      "documented": "Client-supplied reference.",
      "observed": "第三方接受了调用方生成的值。",
      "verdict": "PASS",
      "evidenceIds": ["E-001"]
    },
    "uniqueness": {
      "documented": "Client-supplied reference.",
      "observed": "重复 reference 创建了另一个资源。",
      "verdict": "OBSERVED",
      "evidenceIds": ["E-003"]
    },
    "duplicateBehavior": {
      "documented": "Official documentation does not declare duplicate handling.",
      "observed": "重复 reference 创建了另一个资源。",
      "verdict": "OBSERVED",
      "evidenceIds": ["E-003"]
    },
    "reconciliation": {
      "documented": "The response returns a provider resource ID.",
      "observed": "调用方 reference 与第三方 ID 已关联保留。",
      "verdict": "PASS",
      "evidenceIds": ["E-001"]
    }
  },
  "documented": "Official claim",
  "documentSource": ["https://docs.provider.example/reference#customerReference"],
  "observed": "实测结果或具体的未执行原因",
  "correction": "接入时采用的修订规则",
  "evidenceIds": ["E-001"],
  "notes": []
}
```

Every request field and response field must have a non-empty `type` and an explicit `required` value. Request fields also require `source`; response fields require `action`. Every field and error-code row must have a non-empty `documented` value, at least one `documentSource`, and an explicit `verdict`. Write `observed` and every non-empty `correction` in Chinese. Preserve official wording and protocol literals exactly, embedding literals such as `HTTP 201`, `IN_PROGRESS`, or field names inside the Chinese explanation. When the source is silent, write an explicit absence and reference the pages searched. Use `NOT_EXECUTED` for a documented row that was not tested and `BLOCKED` only when an external condition specifically prevents that row's probe. Only `DOCUMENT_MISMATCH` means that the documented value is replaced in the report.

Every request field must contain `criticalFieldCategory`, using `null` only after deciding that no material profile applies. Material categories are `AMOUNT`, `PHONE`, `ACCOUNT_NUMBER`, `ACCOUNT_NAME`, `CARD`, `IDENTITY`, `INSTITUTION`, `IDENTIFIER`, `ENUM_ROUTING`, `DATETIME`, `TEXT`, and `CALLBACK_SECURITY`.

For a material field, `constraintEvidence` must contain every dimension required by its profile in [test-strategy.md](test-strategy.md). Each dimension contains `documented`, `observed`, `verdict`, and `evidenceIds`. An executed verdict requires evidence; `BLOCKED` or `NOT_EXECUTED` requires a concrete reason in `observed`. `probeDimensions` lists only dimensions actually executed and must point to executed entries in `constraintEvidence`.

Keep all results in the same request-field row. The renderer summarizes the constraint dimensions in the existing constraint cell; `documented`, `observed`, `correction`, and `evidenceIds` remain the human-readable contract and evidence trail.

## Error-code rows

```json
{
  "code": "409 / duplicate reference",
  "verdict": "DOCUMENT_MISMATCH",
  "documented": "409 Conflict",
  "documentSource": ["https://docs.provider.example/errors#duplicate"],
  "observed": "实际返回 HTTP 200，并生成了新的资源 ID。",
  "correction": "不要依赖第三方幂等，需要在接入侧控制重复请求。",
  "evidenceIds": ["E-020"],
  "notes": []
}
```

## Support scope

```json
{
  "verdict": "OBSERVED",
  "official": {
    "catalogMode": "RETRIEVAL",
    "institutions": "Dynamic institution catalog",
    "regions": ["NG"],
    "currencies": ["NGN"],
    "sourceRefs": ["https://docs.provider.example/institutions"]
  },
  "observed": {
    "summary": "Sandbox returned 145 institutions"
  },
  "retrieval": {
    "method": "GET",
    "url": "/v1/institutions",
    "parameters": "country=NG",
    "authentication": "Bearer token",
    "instructions": "Call at startup and refresh daily; preserve provider codes."
  },
  "evidenceIds": ["E-INSTITUTIONS-001"]
}
```

Use `catalogMode: INLINE` when the complete official declaration is practical to display. Use `RETRIEVAL` for large or dynamic data and provide enough official retrieval information for the reader to obtain the current catalog. Keep `official` and `observed` separate.

## Case records

```json
{
  "id": "B-01",
  "name": "Successful request",
  "probeOutcome": "SUCCESS",
  "verdict": "PASS",
  "documented": {},
  "observed": {},
  "request": {},
  "response": {},
  "evidenceIds": ["E-001"],
  "notes": []
}
```

`probeOutcome` is required for every executed case:

- `SUCCESS` — the request reached the interface's documented successful business outcome.
- `FAILURE` — the provider rejected the request or returned a failed business outcome intentionally exercised by the probe.

It is independent of `verdict`: a `SUCCESS` probe can expose a `DOCUMENT_MISMATCH`, and a correctly documented `FAILURE` probe can be `PASS`. Every interface must contain at least one executed case of each outcome. Blocked or unexecuted intentions do not satisfy this coverage.

Requests and responses must be complete enough to implement the interface, but redacted before entering this model.
`bodyRaw` may remain in evidence data when byte-for-byte signing or serialization differences matter, but the HTML report must not display it beside `body`. Treat `redaction` as report metadata and render it as a human-readable note outside the protocol message, never as a request or response field. The note must describe the affected protocol data without exposing internal evidence keys such as `bodyRaw`.

## Cryptographic evidence

Use the same structure for an applicable `signing` or `encryption` dimension:

```json
{
  "official": {
    "sourceRefs": ["https://docs.provider.example/webhooks#signature"],
    "algorithm": "HMAC-SHA512",
    "keySource": "Webhook Secret",
    "message": "Raw HTTP body bytes",
    "encoding": "No reserialization",
    "output": "Lowercase hexadecimal",
    "signatureLocation": "x-provider-signature"
  },
  "localVerification": {
    "runtime": "Python 3 stdlib",
    "testVector": "Synthetic body and disposable key",
    "code": "Executable redacted code",
    "observed": "输出为 128 位十六进制字符；原文验签通过，篡改后验签失败。",
    "verdict": "OBSERVED",
    "evidenceIds": ["E-CRYPTO-001"]
  },
  "interoperability": {
    "observed": "没有可用的真实回调原文和签名。",
    "verdict": "BLOCKED",
    "evidenceIds": []
  }
}
```

Keep sourced official claims, local executable verification, and real provider interoperability separate. Every applicable dimension must include a reusable code example; when official parameters are incomplete, the example must visibly preserve the unresolved placeholders. Local success is `PASS` only when it matches an official expected vector; otherwise use `OBSERVED`. A local encrypt/decrypt round trip alone does not prove provider compatibility. Flat `NOT_APPLICABLE` objects remain valid when no application-level cryptographic operation exists.

## Scenario records

```json
{
  "id": "S-01",
  "name": "Create then query",
  "origin": "requested",
  "requestedScenario": "Create then query",
  "verdict": "PASS",
  "purpose": "Confirm resource correlation and status",
  "steps": [
    {
      "index": 1,
      "interfaceId": "create",
      "action": "Create resource",
      "consumes": ["accessToken"],
      "produces": ["resourceId", "customerReference"],
      "verdict": "PASS",
      "observed": "实际返回 HTTP 201 Created。",
      "evidenceIds": ["E-010"]
    }
  ],
  "notes": []
}
```

`origin` is `requested` or `inferred`. A successful trigger request is not proof that an asynchronous delivery occurred.

Every item in `input.requestedScenarios` must map one-to-one to a distinct scenario record with `origin: "requested"` and the same `requestedScenario` value. Never merge or omit requested scenarios. If execution is impossible or intentionally skipped, keep the record visible with `BLOCKED` or `NOT_EXECUTED` and state the reason in `notes` or a step observation.

Give every step its own verdict. When a step is blocked, mark that step `BLOCKED` and keep its downstream steps as `NOT_EXECUTED`; do not mark the whole chain as if every step failed. Keep the step observation and evidence separate from consumed and produced values.

Use scenario notes only for additional context not already represented by progress, step observations, or evidence. Leave notes empty instead of restating the verdict or blocking reason.

## External questions

```json
{
  "priority": "P0",
  "question": "Confirm whether the Sandbox credential is active for this tenant."
}
```

Use:

- `P0` — must be confirmed; execution or a reliable integration decision is blocked.
- `P1` — should be confirmed; material to implementation quality but not necessarily blocking.
- `P2` — optional clarification; safe for the integration team to ignore.

Do not leave external questions as unprioritized strings.

## Findings

```json
{
  "severity": "P0",
  "category": "DOCUMENT_MISMATCH",
  "interfaceId": "create",
  "documented": "409 for duplicate reference",
  "observed": "实际返回 HTTP 200，并生成了新的资源 ID。",
  "correction": "在接入侧实现幂等控制。",
  "evidenceIds": ["E-020", "E-021"]
}
```

Every runtime assertion needs an evidence ID. Recommendations must remain visibly distinct from observations.

## Terminology

- Use the current provider's canonical name throughout prose.
- Keep internal channel names separate from provider names.
- Preserve protocol literals exactly.
- Use one business term for one resource within a report.
- Do not silently rename IDs, references, events, statuses, or headers.
