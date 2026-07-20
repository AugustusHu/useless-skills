---
name: debug-third-party-api
description: Validate third-party API documentation against real test-environment behavior and produce a consistent single-file HTML evidence report. Use when Codex must extract a documentation URL, executable test environment, interface scope, and optional scenarios; inspect official contracts; call in-scope APIs; compare documented and observed behavior; explain cross-interface flows; or report ambiguities, errors, signing, encryption, supported institutions, regions, and external questions.
---

# Third-Party API Debug

Produce a trustworthy implementation contract, not a document summary.

## Required inputs

Extract four elements before testing:

1. Official third-party documentation location.
2. Executable test-environment information.
3. Interface scope for this run.
4. Requested test scenarios, when supplied.

Normalize them using [input-contract.md](references/input-contract.md). Ask only for missing information that prevents execution or a meaningful result. Never persist credential values; retain references such as `ENV:CLIENT_SECRET`.

When a documentation link is on Yuque, fetch it with `scripts/yuque_doc.py read <url> --output <temporary.md> --meta-output <temporary.json>` and extract the four inputs from the saved Markdown. Use `pull` only when adjacent knowledge-base documents are relevant. Use `update` only when the user explicitly asks to write back to Yuque.

## Required outcomes

- Establish the documented contract for every in-scope interface.
- Capture real request and response evidence for every executable in-scope interface.
- Execute at least one valid success probe and one deliberate failure probe for every interface. Treat this pair as the minimum coverage, not the target; continue with material field, error, state, signing, idempotency, and boundary probes.
- Correct documented fields in place and label every correction with evidence.
- Preserve protocol literals exactly, including field casing, headers, enums, and event names.
- Explain authentication, signing, encryption, errors, support scope, limitations, and external questions.
- Where signing, verification, encryption, or decryption applies, separate the official algorithm contract, executable local code verification, and real provider interoperability. Never treat a local round trip as proof of provider compatibility.
- Prioritize probes for critical request fields in financial APIs. Cover, at minimum: amount minimum/maximum, unit, and format; phone-number format and supported countries; account-number format; and account-name format. Extend this set when other fields can materially affect transaction validity or routing.
- Treat date/time fields as precision-sensitive. Verify the exact format and timezone; for timestamps, verify number vs string and seconds vs milliseconds.
- Show useful cross-interface scenarios and data flow without claiming unobserved behavior.
- Produce one self-contained HTML report with one tab per interface.

Use [evidence-model.md](references/evidence-model.md) as the report-data contract and [test-strategy.md](references/test-strategy.md) to choose tests.

## Judgment

Prefer official machine-readable sources, then official prose. Treat documentation as a hypothesis and runtime evidence as observation.

Choose tools and probes appropriate to the provider. Do not force a universal HTTP runner or fixed test sequence. Treat the debug environment as sandbox by definition and execute the in-scope requests needed to validate the contract, including financial, onboarding or account-opening, resource-creation, and state-transition operations.

Infer interface relationships from produced and consumed values such as tokens, resource IDs, references, statuses, and webhook events. Add scenario tests when they materially explain the integration.

The interface scope authorizes all calls against the supplied debug environment. Do not classify the environment, request confirmation, or skip execution because an operation creates test data, moves test funds, opens a test account, or changes test state. Record every created resource or external side effect.

Use `BLOCKED` only for a concrete missing external condition, missing provider permission, or unavailable dependency. Treat a received provider rejection as executed runtime evidence, not as blocked. Use `NOT_EXECUTED` only when the user excluded the test or execution became impossible after an identified prerequisite failed. Never use either verdict solely because the interface is financial, account-opening, state-changing, or otherwise side-effecting.

## Context discipline

Keep raw pages, requests, responses, and headers in temporary evidence files. Bring only the active interface contract, current scenario, redacted observation, and unresolved differences into context. Preserve evidence IDs and paths so the final report remains traceable.

Redact credentials, authorization values, private keys, signatures, personal data, and signed download URLs before displaying tool output or building report data.

## Report contract

Build a JSON result conforming to [evidence-model.md](references/evidence-model.md). Render it with:

```bash
python3 scripts/render_report.py run.json report.html
python3 scripts/validate_report.py run.json report.html
```

Use only these verdict terms:

- `PASS` — observation matches the claimed contract.
- `DOCUMENT_MISMATCH` — observation contradicts documentation or the requirement.
- `OBSERVED` — useful behavior without a reliable documented expectation.
- `BLOCKED` — missing external condition prevents execution.
- `NOT_APPLICABLE` — the dimension does not apply.
- `NOT_EXECUTED` — excluded by the user or unreachable after a failed prerequisite.

The renderer and validator hard-gate required interface structure, per-interface success/failure probe coverage, report sections, requested-scenario coverage, verdict validity, financial probe dimensions, external-question priority, and secret hygiene.

Review the parts that still require judgment:

- every executed claim points to evidence;
- every request-field, response-field, and error-code row has an explicit verdict; use `DOCUMENT_MISMATCH` only for an actual contradiction;
- scenario steps show inputs, outputs, dependencies, side effects, an explicit verdict, and evidence; blocked flows identify the exact blocking step and leave downstream steps visible as not executed; scenario notes add only information not already shown by progress or steps;
- corrections distinguish documented, observed, and recommended behavior;
- terminology is consistent and protocol literals are unchanged;
- limitations, side effects, and external questions are accurate and explicit.
