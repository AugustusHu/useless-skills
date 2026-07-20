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

## Field rows

Use the same keys for request and response rows:

```json
{
  "field": "customerReference",
  "type": "string",
  "required": true,
  "verdict": "PASS",
  "criticalFieldCategory": null,
  "probeDimensions": [],
  "documented": "Official claim",
  "observed": "Runtime observation or Not executed",
  "correction": "Implementation contract",
  "evidenceIds": ["E-001"],
  "notes": []
}
```

Every request field, response field, and error-code row must have an explicit
`verdict`. Use `NOT_EXECUTED` for a documented row that was not tested and
`BLOCKED` only when an external condition specifically prevents that row's
probe. Only `DOCUMENT_MISMATCH` means that the documented value is replaced in
the report.

For financial request fields, set `criticalFieldCategory` to `AMOUNT`, `PHONE`, `ACCOUNT_NUMBER`, or `ACCOUNT_NAME`, and list the tested constraints in `probeDimensions`.

- `AMOUNT` includes at least `minimum`, `maximum`, `unit`, and `format`.
- `PHONE` includes at least `format` and `supportedCountries`.
- `ACCOUNT_NUMBER` and `ACCOUNT_NAME` include at least `format`.

Keep the results in the same request-field row. Use `documented`, `observed`, `correction`, and `evidenceIds` to summarize the independently executed probes. Dimensions blocked by a concrete missing external condition remain explicit in `observed`; do not create a separate financial-field report section.

## Error-code rows

```json
{
  "code": "409 / duplicate reference",
  "verdict": "DOCUMENT_MISMATCH",
  "documented": "409 Conflict",
  "observed": "200 with a new resource ID",
  "correction": "Do not rely on provider-side idempotency",
  "evidenceIds": ["E-020"],
  "notes": []
}
```

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
    "source": "Official documentation page",
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
    "observed": "128 hex characters; replay accepted; tamper rejected",
    "verdict": "OBSERVED",
    "evidenceIds": ["E-CRYPTO-001"]
  },
  "interoperability": {
    "observed": "No real callback body or signature was available",
    "verdict": "BLOCKED",
    "evidenceIds": []
  }
}
```

Keep official claims, local executable verification, and real provider interoperability separate. Local success is `PASS` only when it matches an official expected vector; otherwise use `OBSERVED`. A local encrypt/decrypt round trip alone does not prove provider compatibility. Flat `NOT_APPLICABLE` objects remain valid when no application-level cryptographic operation exists.

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
      "observed": "201 Created",
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
  "observed": "200 and a new resource ID",
  "correction": "Enforce idempotency on the client",
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
