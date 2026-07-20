---
name: debug-third-party-api
description: Validate third-party API contracts against test-environment behavior and produce a single-file HTML evidence report. Use for scoped API probing, documented-vs-observed comparison, cross-interface flows, errors, cryptography, support scope, and integration questions.
---

# Third-Party API Debug

Turn documentation and runtime evidence into a trustworthy implementation contract.

## Required inputs

Extract four elements before testing:

1. Official third-party documentation location.
2. Executable test-environment information.
3. Interface scope for this run.
4. Requested test scenarios, when supplied.

Normalize them with [input-contract.md](references/input-contract.md). Ask only for missing information that blocks execution or a meaningful result. Keep credential references such as `ENV:CLIENT_SECRET`, never values.

When a documentation link is on Yuque, fetch it with `scripts/yuque_doc.py read <url> --output <temporary.md> --meta-output <temporary.json>` and extract the four inputs from the saved Markdown. Use `pull` only when adjacent knowledge-base documents are relevant. Use `update` only when the user explicitly asks to write back to Yuque.

## Required outcomes

- Extract exact official fields, constraints, enums, examples, errors, and sources for every in-scope interface. Record official silence explicitly.
- Execute at least one success probe and one deliberate failure probe per interface, then apply [test-strategy.md](references/test-strategy.md) to additional risks.
- Capture complete, redacted request and response evidence for every executed probe.
- Correct documented fields in place and attach evidence; preserve field casing, headers, enums, event names, and other protocol literals.
- Write observations and integration corrections in Chinese without translating protocol literals.
- Put system regions only in the overview, for example `支持尼日利亚、菲律宾、俄罗斯。`, and institutions only on relevant interfaces. Omit currency catalogs from support scope; test currency fields and amount constraints normally.
- State authentication, limitations, and external questions.
- For signing or encryption, separate the official contract, local code verification, and real provider interoperability. Include reusable code and never treat a local round trip as interoperability proof.
- Classify material request fields before testing. Keep every required constraint dimension in its field row with the official claim or absence, observation or non-execution reason, verdict, and evidence.
- Show useful cross-interface flows without claiming unobserved behavior.
- Produce one self-contained HTML report with one tab per interface.

Use [evidence-model.md](references/evidence-model.md) as the report-data contract and [test-strategy.md](references/test-strategy.md) to choose tests.

## Judgment

Prefer official machine-readable sources, then official prose. Treat documentation as a hypothesis and runtime evidence as observation.

Choose provider-appropriate tools and probes instead of a fixed runner or sequence. Treat the supplied debug environment as sandbox and the interface scope as authorization to execute its calls, including financial, onboarding, resource-creation, and state-transition operations. Record every external side effect and resource ID.

Use `BLOCKED` only for a missing external condition, provider permission, or dependency. A provider rejection is runtime evidence. Use `NOT_EXECUTED` only for user exclusion or an unreachable step after a failed prerequisite; side effects alone justify neither verdict.

## Context discipline

Keep raw pages, requests, responses, and headers in temporary evidence files. Load only the active contract, scenario, redacted observation, and unresolved differences into context. Preserve evidence IDs and paths.

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

The validator enforces report structure, probe and scenario coverage, verdicts, material-field evidence, question priority, and secret hygiene.

Review the parts that still require judgment:

- executed claims point to evidence;
- field and error rows have sources and explicit verdicts; only actual contradictions use `DOCUMENT_MISMATCH`;
- scenario steps preserve inputs, outputs, dependencies, verdicts, and evidence; blocked flows keep downstream steps visible as `NOT_EXECUTED`;
- documented, observed, and recommended behavior remain distinct;
- terminology, limitations, side effects, and external questions are accurate.
