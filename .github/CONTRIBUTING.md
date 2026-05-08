# Contributing

Thank you for helping improve Tilly Engineer Skills.

TES is a reference package for assisted context meshes, adapter surfaces,
project-scoped helper runtimes, Cortex, MCP, and Field Reports. Contributions
should keep the package portable, local-first, and auditable.

## Before You Change Code

1. Read [AGENTS.md](../AGENTS.md).
2. Classify the change:
   - maintainer-only validator or documentation;
   - delivered installer/helper behavior;
   - adapter source under `src/**`;
   - governed docs under `docs/**`.
3. Keep the repository root thin. Do not add installable source copies to root
   hidden folders such as `.agents`, `.claude-plugin`, `.cursor`, or `skills`.
4. Do not add tag, release, publish, marketplace, live GitHub issue, global
   install, or global config behavior without explicit maintainer approval.

## Local Verification

Run the smallest focused gate first. Before proposing a material package
change, run:

```bash
npm run commit:check
```

Useful focused gates:

```bash
python3 scripts/validate_reference_package.py
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/github_readiness_oracle.py --self-test
python3 scripts/install_smoke.py --self-test
python3 scripts/tes_init.py --self-test
python3 scripts/tes_update.py --self-test
python3 scripts/materialize_adapter.py all --check
```

## Pull Requests

Pull requests should include:

- what changed;
- which consumer is affected;
- which oracle or evidence proves it;
- whether any release, publishing, marketplace, or live transport behavior is
  intentionally deferred.

Do not include secrets, private project code, local Field Reports payloads,
or raw canary worktrees in a pull request.
