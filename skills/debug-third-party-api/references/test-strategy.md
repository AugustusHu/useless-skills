# Test strategy

Build enough independent runtime evidence to establish an implementable contract and expose material risk.

## Interface coverage

Every interface requires, at minimum:

- one valid request that reaches the documented successful business outcome;
- one deliberately invalid request that reaches a provider rejection or documented failed business outcome.

Record these as `probeOutcome: SUCCESS` and `probeOutcome: FAILURE`. This describes the API outcome, independently of the documentation verdict. Then probe the material dimensions that apply:

- authentication absence or invalidity;
- required-field, type, enum, and boundary behavior;
- documented error cases;
- response shape and content type;
- idempotency and duplicate references;
- signing and encryption fidelity;
- interface-level institution catalogs and system-level region support when relevant.

Two probes are only the floor. Do not convert untested dimensions into broad conclusions after the minimum pair. Prefer a valid baseline with one material variable changed, and add cases while new probes can resolve material uncertainty.

## Official contract collection

Before testing, collect the original official declaration for every request field, response field, and error code: name, type, requiredness, constraints, enums, examples, conditional rules, and exact source page or section. Also identify each request field's source or generation rule and each response field's integration action or mapping. When the official material is silent or contradictory, record that fact with the pages searched; do not replace it with an inferred declaration.

Collect official region support once at system level and summarize it in the report overview with full Chinese names, for example `支持尼日利亚、菲律宾、俄罗斯。` Do not repeat regions per interface. Collect institution support only for interfaces that select, return, or depend on institutions, keeping official declarations separate from runtime observations. Keep complete small institution catalogs inline. For large or dynamic catalogs, record the official list/query interface or documentation route, method, parameters, authentication, and usage instructions so the reader can retrieve the current data.

Do not collect or render a currency catalog as a support-scope dimension. When an interface contains a currency field or transfers an amount, validate currency through that field's documented contract and the `AMOUNT` or routing constraint evidence.

## Material field constraints

Before choosing cases, read [material-field-profiles.json](material-field-profiles.json), the canonical material-field profile catalog. Use `appliesWhen` for semantic classification; treat `fieldNamePattern` only as a detection hint. Probe every entry in the selected profile's `dimensions` object independently. Update the JSON instead of duplicating profiles in Markdown or Python.

Use a valid baseline and change one dimension at a time. In the supplied test environment, execute the write or lifecycle operation needed to establish each material boundary. Reuse the resulting test resource across related probes when that preserves independence, and use documented cleanup or reversal interfaces when they are part of the scope.

For every request field, explicitly decide whether a material profile applies; do not omit `criticalFieldCategory`. For a material field, copy every configured dimension into `constraintEvidence`. An untested or undocumented dimension remains explicit with its own verdict and reason. Summarize the result in the existing request-field row under documented, observed, correction, and evidence; do not create a separate constraint report.

## Scenario coverage

Infer relationships from outputs consumed by later interfaces. Useful patterns include:

- authenticate → create → query;
- create → query by ID/reference;
- create → cancel/refund → query;
- create → callback failure → resend → callback;
- invalid token → refresh → safe retry;
- duplicate create → idempotency observation;
- create response ↔ query response ↔ webhook payload consistency;
- concurrent or repeated resources → isolation;
- pending → terminal transition and timeout convergence.

Show the relationship even when a step is blocked. Do not invent responses.

## Cryptographic operations

For signing, verification, encryption, and decryption, capture the sourced official algorithm contract before testing: algorithm, key source, exact input bytes or canonicalization, character encoding, output encoding, and signature/ciphertext location. Include mode, padding, IV or nonce, authentication tag, and AAD when applicable.

Use an official test vector when available. Otherwise run a synthetic local vector with disposable values and record the reusable executable code, runtime, result, tamper behavior, and evidence ID. If the official contract is incomplete, provide a code template that marks the unresolved parameters rather than inventing them. Keep real provider interoperability as a separate verdict: a local HMAC match or encrypt/decrypt round trip proves local consistency, not compatibility with the provider. Use only redacted key references for real secrets.

## Side-effect classes

- `READ_ONLY`: documentation, lists, queries.
- `AUTH`: credential exchange.
- `TEST_CREATE`: sandbox resource creation.
- `CALLBACK_TRIGGER`: resend or callback simulation.
- `FINANCIAL`: payment, refund, payout.
- `EXTERNAL_WORK`: messages, identity checks, field work, logistics.
- `DESTRUCTIVE`: cancel, delete, revoke.

The debug environment is sandbox by definition. The interface scope authorizes every listed class; category alone is never a reason to skip a test. Record IDs and counts for every created test resource.

## Evidence quality

Capture the exact method, URL, relevant headers, query, path, body, HTTP status, content type, correlation/request ID, response body, timestamp, and redaction note. Keep raw evidence out of the conversational context.

Use `BLOCKED` only when a named external condition prevents the call. Use `NOT_EXECUTED` only when the user excluded the test or a failed prerequisite made it unreachable. A financial, account-opening, state-changing, or externally visible test is not blocked merely because of its side-effect class.
