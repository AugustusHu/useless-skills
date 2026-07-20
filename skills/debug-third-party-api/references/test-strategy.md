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
- support lists, institutions, currencies, countries, or regions when relevant.

Two probes are only the floor. Do not convert untested dimensions into broad conclusions after the minimum pair. Prefer a valid baseline with one material variable changed, and add cases while new probes can resolve material uncertainty.

## Financial critical fields

Identify material request fields before choosing cases. Mark applicable fields as `AMOUNT`, `PHONE`, `ACCOUNT_NUMBER`, or `ACCOUNT_NAME`, then probe each material constraint separately.

- `AMOUNT`: minimum, maximum, unit or currency, representation unit, precision or scale, accepted format, zero/negative handling, and boundary behavior.
- `PHONE`: accepted format, country-code handling, normalization, and supported countries.
- `ACCOUNT_NUMBER`: length, character set, leading-zero handling, whitespace or separator handling, and provider-specific checksum or format when documented.
- `ACCOUNT_NAME`: length, character set, Unicode/local-language support, whitespace normalization, and case or punctuation handling when material.

Use a valid baseline and change one dimension at a time. In the supplied test environment, execute the write or lifecycle operation needed to establish each material boundary. Reuse the resulting test resource across related probes when that preserves independence, and use documented cleanup or reversal interfaces when they are part of the scope.

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

The debug environment is sandbox by definition. The interface scope authorizes every listed class; category alone is never a reason to skip a test. Record IDs and counts for every created test resource.

## Evidence quality

Capture the exact method, URL, relevant headers, query, path, body, HTTP status, content type, correlation/request ID, response body, timestamp, and redaction note. Keep raw evidence out of the conversational context.

Use `BLOCKED` only when a named external condition prevents the call. Use `NOT_EXECUTED` only when the user excluded the test or a failed prerequisite made it unreachable. A financial, account-opening, state-changing, or externally visible test is not blocked merely because of its side-effect class.
