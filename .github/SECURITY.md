# Security Policy

TES is local-first. It should not send source code, secrets, private paths, or project-owned governance to external systems without explicit user authorization.

## Reporting A Vulnerability

If GitHub private vulnerability reporting is available for this repository, use it.

If it is not available, open a minimal public issue that requests a private security channel. Do not include exploit details, tokens, private repository paths, payload bodies, or sensitive project context in a public issue.

## Supported Surface

Security review currently covers:

- assisted installation behavior;
- adapter materialization;
- project-scoped `.tes/bin/**` helpers;
- read-only Cortex MCP server behavior;
- Field Reports sanitization, suppression, fake transport, and receiver quarantine;
- repository validation and documentation gates.

Partial or deferred surfaces are not treated as production security claims:

- real GitHub issue publication for Field Reports;
- marketplace submission;
- live platform plugin activation;
- optional vector/Xenova behavior;
- write-capable MCP tools.

## Sensitive Data Rules

Do not submit:

- secrets, tokens, credentials, or API keys;
- private project source code;
- raw `.tes/field-reports/**` transport state;
- raw canary clones or logs containing private paths;
- payloads captured from live systems.

Use redacted examples and describe reproducible local steps instead.
