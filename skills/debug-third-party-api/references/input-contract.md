# Input contract

Represent the four task elements without provider-specific assumptions.

```json
{
  "documentation": [
    {
      "url": "https://docs.provider.example/reference",
      "kind": "api-reference",
      "official": true
    }
  ],
  "environment": {
    "name": "Test",
    "baseUrl": "https://sandbox.provider.example",
    "credentialRefs": ["ENV:TEST_CLIENT_ID", "ENV:TEST_CLIENT_SECRET"],
    "authenticationHint": null,
    "callback": {
      "urlRef": "ENV:TEST_CALLBACK_URL",
      "secretRef": "ENV:TEST_WEBHOOK_SECRET"
    },
    "network": {},
    "testData": {},
    "constraints": {
      "production": false,
      "billable": null,
      "createsExternalWork": null
    }
  },
  "interfaceScope": [
    {
      "requestedName": "Create resource",
      "methodHint": "POST",
      "pathHint": "/resources"
    }
  ],
  "requestedScenarios": []
}
```

## Completeness

- Missing documentation location blocks contract validation.
- A Yuque documentation URL may contain some or all four inputs. Keep the original browser URL in `documentation`, fetch its Markdown to temporary evidence with `scripts/yuque_doc.py`, and derive inputs from that local copy.
- Missing interface scope blocks task boundaries.
- Missing environment or credentials permits documentation-only analysis; mark executable tests `BLOCKED`.
- Missing callback information blocks callback delivery and signature observations, not unrelated synchronous tests.
- Missing scenarios does not block the run. Infer only scenarios that improve understanding or cover material risk, and label them `inferred`.

## Sensitive information

Replace values with runtime references. Do not copy secrets from a requirement into result JSON, evidence indexes, commands shown to the user, or the report.

Allowed references:

- `ENV:VARIABLE_NAME`
- `FILE:/secure/path`
- `KEYCHAIN:item-name`
- `[REDACTED]`

## Execution semantics

The supplied debug environment is sandbox by definition. Set `environment.constraints.production` to `false`; do not classify the environment or ask for confirmation. The interface scope authorizes all listed calls, including write, financial, account-opening, and state-transition interfaces.
