# Test strategy

Select the smallest set that establishes an implementable contract and exposes material risk.

## Interface coverage

Consider:

- one valid request;
- authentication absence or invalidity;
- required-field, type, enum, and boundary behavior;
- documented error cases;
- response shape and content type;
- idempotency and duplicate references;
- signing and encryption fidelity;
- support lists, institutions, currencies, countries, or regions when relevant.

Do not run meaningless combinations. Prefer a valid baseline with one material variable changed.

## Financial critical fields

Identify material request fields before choosing cases. Mark applicable fields as `AMOUNT`, `PHONE`, `ACCOUNT_NUMBER`, or `ACCOUNT_NAME`, then probe each material constraint separately.

- `AMOUNT`: minimum, maximum, unit or currency, representation unit, precision or scale, accepted format, zero/negative handling, and boundary behavior.
- `PHONE`: accepted format, country-code handling, normalization, and supported countries.
- `ACCOUNT_NUMBER`: length, character set, leading-zero handling, whitespace or separator handling, and provider-specific checksum or format when documented.
- `ACCOUNT_NAME`: length, character set, Unicode/local-language support, whitespace normalization, and case or punctuation handling when material.

Use a valid baseline and change one dimension at a time. Prefer validation-only endpoints and non-production environments. Do not create a real payment, payout, refund, or other financial side effect merely to discover a field boundary. When a probe is unsafe or externally blocked, record it as `BLOCKED` or `NOT_EXECUTED` with the reason instead of omitting it.

Run constraint dimensions independently so one result does not mask another. Summarize them in the existing request-field row under documented, observed, correction, and evidence; do not create a separate financial-field report section.

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

For signing, verification, encryption, and decryption, capture the official algorithm contract before testing: algorithm, key source, exact input bytes or canonicalization, character encoding, output encoding, and signature/ciphertext location. Include mode, padding, IV or nonce, authentication tag, and AAD when applicable.

Use an official test vector when available. Otherwise run a synthetic local vector with disposable values and record the executable code, runtime, result, tamper behavior, and evidence ID. Keep real provider interoperability as a separate verdict: a local HMAC match or encrypt/decrypt round trip proves local consistency, not compatibility with the provider. Use only redacted key references for real secrets.

## Side-effect classes

- `READ_ONLY`: documentation, lists, queries.
- `AUTH`: credential exchange.
- `TEST_CREATE`: sandbox resource creation.
- `CALLBACK_TRIGGER`: resend or callback simulation.
- `FINANCIAL`: payment, refund, payout.
- `EXTERNAL_WORK`: messages, identity checks, field work, logistics.
- `DESTRUCTIVE`: cancel, delete, revoke.
- `PRODUCTION_MUTATION`: any production write.

Run production mutations only with explicit authorization. Treat financial and external-work tests as blocked until their sandbox behavior is clear. Record IDs and counts for every created test resource.

## Evidence quality

Capture the exact method, URL, relevant headers, query, path, body, HTTP status, content type, correlation/request ID, response body, timestamp, and redaction note. Keep raw evidence out of the conversational context.

Use `BLOCKED` when the missing condition is external. Use `NOT_EXECUTED` when the test was intentionally omitted. Neither is a failure.
