---
tds_id: roadmap.goal_super_spec_agent_hooks_shell_intent_and_redaction
tds_class: roadmap
status: proposed
consumer: maintainers, hook authors, oracle authors, canary operators, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: Agent Hooks Shell Intent And Redaction

Status: proposed execution packet for one isolated window.

Run this SPEC with `tes-host-transcript-canary`. The final product claim cannot
close as `PASS_CEILING` without host-real transcript evidence and the
post-execution gate.

## New-Window Prompt

```text
/goal Execute docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-agent-hooks-shell-intent-and-redaction.md with tes-host-transcript-canary. Use a dedicated branch or worktree, preserve unrelated changes, patch TES source only, run the focused red-capable oracles first, rebuild package identity if delivered behavior changes, and stop only at CERTIFIED, NEEDS_HOST_TRANSCRIPT_CANARY, or a named blocker.
```

## Senior Framing

Protected baseline: structured `Edit` and `apply_patch` on governed artifacts
already produce `supervise`; routine non-governed actions stay quiet.

The current gap is not that Mantra Gate is weak. It is that the kernel sees
structured payloads but not common shell mutation intent. Closing this gap must
not introduce a new leak path: the same loop must prevent raw command/path data
from reaching stderr, Cursor messages, or the hook ledger.

Classification: `Platform`. This touches delivered PreToolUse runtime behavior,
host hook semantics, source oracles, installed target evidence, and release
identity.

## Findings Owned

- H-03: shell writes to governed surfaces are silently allowed.
- BUG-04: unknown mutating tools cannot reach `needs_discoverability` when the
  governed path is hidden in shell payload.
- BUG-05: `routine -> material` escalation and `supervise` are dead for shell
  governed mutations.
- BUG-08: root `SKILL.md` is not treated as governed when the host passes the
  bare filename.
- BUG-03: forbidden block reasons may echo raw command text.
- BUG-06: ledger path may retain secret-like values.

## Non-Goals

- Do not build a full shell interpreter.
- Do not flatten Claude, Codex, and Cursor renderer contracts.
- Do not block routine shell commands that do not touch governed surfaces.
- Do not rely on one literal command list as the only protection.
- Do not patch installed target mirrors as source of truth.

## Execution Rules

- Use a dedicated branch or worktree. Do not commit directly on shared `main`
  while another parallel spec is active.
- If another spec changes `scripts/pretooluse_kernel.py`,
  `scripts/tes_install.py`, or `docs/architecture/PRETOOLUSE-CONTRACT.md`,
  rebase and rerun all focused gates before closing.
- Patch source first: `scripts/pretooluse_kernel.py`, then the source oracle
  that owns PreToolUse behavior. Touch `scripts/tes_install.py` only for
  renderer or ledger redaction.
- Use official host docs only to confirm payload field names; do not widen
  behavior from stale memory.

## SPEC-000: Reproduce The Red State

Required probes before editing:

```bash
PYTHONPATH=scripts python3 - <<'PY'
import pretooluse_kernel as k

def risk(action, paths):
    text = action.lower()
    if "push --force" in text or "rm " in text:
        return "forbidden"
    if any(token in text for token in ("write", "edit", "delete", "append", "cat payload")):
        return "material"
    return "routine"

cases = [
    ("Bash", {"command": "echo x >> CLAUDE.md"}, "supervise"),
    ("Bash", {"command": "sed -i s/a/b/ AGENTS.md"}, "supervise"),
    ("Bash", {"command": "cat payload > .cursor/rules/x.mdc"}, "supervise"),
    ("Edit", {"file_path": "SKILL.md"}, "supervise"),
]
for tool, payload, expected in cases:
    got = k.decide_pretooluse({"tool_name": tool, "tool_input": payload}, risk_classifier=risk, marker="MARK")
    print(tool, payload, got["outcome"], "expected", expected)
PY
```

Expected before fix: at least the shell cases and bare `SKILL.md` show `allow`.
If they are already green, stop and audit drift instead of patching.

## SPEC-001: Governed Path Detection

Required behavior:

- `CLAUDE.md`, `AGENTS.md`, `docs/adr/**`, `docs/governance/**`,
  `.cursor/rules/**`, and any `SKILL.md` path segment are governed.
- Bare `SKILL.md`, `./SKILL.md`, nested `docs/x/SKILL.md`, and absolute
  `.../SKILL.md` all match; `MYSKILL.md` and `SKILLS.md` do not.
- Shell redirects and common file operands extract target paths conservatively:
  `>`, `>>`, `tee`, `tee -a`, `sed -i`, `rm`, `cp`, `mv`, and equivalent simple
  command forms.
- Ambiguous shell payloads that plausibly mutate a governed surface become
  `supervise` or `needs_discoverability`, not silent `allow`.

Implementation guidance:

- Prefer a small tokenizer/parser helper in `pretooluse_kernel.py`.
- Keep the helper data-driven by governed surface matching plus mutation shape.
- Record classifier trace fields that explain shell path extraction without
  storing raw command text.

## SPEC-002: Redaction At Boundary

Required behavior:

- Forbidden block reasons do not interpolate raw shell command or raw path.
- Claude/Codex stderr and Cursor `agent_message` receive category-level
  messages.
- Ledger entries do not persist secret-like path segments or raw command text.
- Ledger keeps useful audit value: command category, governed-surface flag,
  redaction count, and stable non-sensitive path class or hash when safe.

Red fixtures:

- Command includes a token-like URL credential and must not appear in stderr or
  Cursor JSON.
- Path includes secret-like text and must not appear in
  `.tes/runtime/hooks/executed.jsonl`.

## SPEC-003: Source Oracles

Update the focused source oracle that owns PreToolUse. It must fail before the
fix and pass after:

```bash
python3 scripts/pretooluse_contract_oracle.py --self-test
python3 scripts/pretooluse_kernel_oracle.py
python3 scripts/hook_audit_prompt_oracle.py --self-test
```

Also run:

```bash
python3 scripts/tes_install.py --self-test
python3 scripts/host_runtime_matrix_oracle.py --self-test
python3 scripts/materialize_adapter.py all --check
```

## SPEC-004: Host Canary

Install the rebuilt local package into a clean target and run one host command
that attempts shell mutation of a governed artifact. The host transcript must
show the command was attempted and the resulting hook behavior was observed.

Required harness chain:

```bash
python3 .agents/skills/tes-host-transcript-canary/scripts/host_canary_loop.py \
  --repo . \
  --target <target> \
  --command '<safe host command label executes shell governed mutation probe>' \
  --command-label 'agent-hooks-shell-governed-mutation' \
  --include-subagents \
  --require-tool-use \
  --mode ceiling-replay \
  --claim-mode ceiling-replay \
  --require-fresh \
  --enforce-same-command
```

Retain only sanitized hashes/statuses. Do not stage raw transcript JSONL.

## SPEC-005: Release Identity And Closeout

Delivered behavior changed. Unless Murillo explicitly forbids it:

```bash
python3 scripts/tes_bump.py patch --yes --json
python3 scripts/tes_bundle.py publish --adapter all --allow-dirty --gate
python3 scripts/build_public_docs.py
python3 scripts/public_bundle_oracle.py
python3 scripts/validate_reference_package.py
npm run commit:check
```

Before any final `PASS`/`CERTIFIED` claim:

```bash
python3 .agents/skills/tes-host-transcript-canary/scripts/post_execution_gate.py \
  --evidence <sanitized-evidence.json> \
  --json-only
```

Acceptance: `supervise` or `needs_discoverability` replaces shell false allow,
no raw secret-like command/path leaks, source/package gates pass, and the
host-backed replay supports the same claim.
