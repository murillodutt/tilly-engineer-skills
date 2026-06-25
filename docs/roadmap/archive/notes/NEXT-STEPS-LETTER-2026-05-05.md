---
tds_id: roadmap.next_steps_2026_05_05
tds_class: roadmap
title: Next Window Reentry Letter
date: 2026-05-05
status: archived
consumer: next engineering session
source_of_truth: false
evidence_level: L0
scope: tilly-engineer-skills v0.1.0 continuation
evidence:
  - npm run commit:check
  - npm run tds:validate
  - npm run materialize:all
  - quick_validate.py src/adapters/codex/skills/tes-engineering-discipline
---

# Next Window Reentry Letter

Status note, 2026-05-06: this letter is retained as historical planning context. Several items below are now closed by later commits, including behavior runner execution, retained Codex evidence, local Claude plugin oracle, reference graph validation, Cortex MCP activation, and installer smoke gates. Use `docs/tds/DOCS-INDEX.yml` and the latest evidence reports for current authority.

Future Codex,

you are entering a project that has just crossed an important threshold. Treat `~/Dev/tilly-engineer-skills` as an independent v0.1.0 reference package, not as an extracted guideline folder. The working thesis is now concrete: source lives in `src/**`, explanation and governance live in `docs/**`, generated install trees live in ignored `dist/**`, and local gates prove that the three adapter outputs can still be materialized.

Do not restart the architecture debate unless the evidence forces it. The root has already been made intentionally thin. `src/adapters/**` is the canonical source for Codex, Claude, and Cursor. `docs/tds/**` is the governed documentation layer. `scripts/materialize_adapter.py` is the bridge from source to installable shape. `scripts/validate_tds.py` is the first documentation governance oracle. This is a strong baseline, and the next work should build on it instead of reshuffling it.

Begin the new window with a quiet reentry:

```bash
cd ~/Dev/tilly-engineer-skills
git status --short --branch --untracked-files=all
git log -5 --oneline
npm run commit:check
python3 $CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-engineering-discipline
git diff --cached --stat
```

If the current staged patch is still present and the checks are green, seal it with a semantic local commit. The recommended message is:

```text
Structure source adapters, TDS, and materialization gates
```

Use that wording because the patch is not only a materializer, not only a docs change, and not only a folder move. It defines the package as an engineering system: source adapters, governed docs, reproducible output, and local gates. Do not push. No remote action has been authorized.

After the commit, do not immediately add another architecture layer. First read the state that the commit produced. Run `npm run commit:check` again, inspect `docs/tds/DOCS-INDEX.yml`, and confirm that `docs/roadmap/**` remains `source_of_truth: false`. The roadmap is guidance, not law. Active contracts are in `AGENTS.md`, `docs/tds/TDS-SPEC.md`, `docs/architecture/PROJECT-STRUCTURE.md`, `docs/adapters/MATERIALIZATION.md`, `docs/governance/AGENTIC-ALIGNMENT-GOVERNANCE.md`, and `docs/mesh/PRINCIPLES.md`.

Remember that versioning and changelog are intentionally implicit in Git. The package baseline lives in `package.json`; semantic history lives in commits. Do not create `CHANGELOG.md`, diary files, or historical drawers to restate what Git already records. If a release summary becomes necessary, make it an evidence report tied to an explicit commit range.

The current alignment across the three nuclei is good, but asymmetric by design. Codex is the primary and most mature derivation: it has a bootloader, a progressive skill, references, an oracle, runtime-aware materialization, and validation. Cursor is intentionally simple: the always-on rule is the correct shape for that tool, and its job is to preserve the four gates without pretending to be a full skill system. Claude is structurally aligned: it has `CLAUDE.md`, plugin metadata, and a Claude skill source, but it still needs an external packaging or installer oracle before anyone calls it distribution certified.

That distinction matters. Do not force fake symmetry between the tools. The shared truth is behavioral, not packaging-level sameness. The four gates, success formula, context mesh method, and TDS evidence discipline are the common contract. The adapters are reductions into each tool's natural shape.

The first post-commit technical wave should be graph validation. The materializer already blocks source-only references from leaking into generated adapter outputs, but the package still needs a broader reference validator. Add a small script, likely `scripts/validate_reference_graph.py`, that parses Markdown links and path-like references across `docs/**`, `src/**`, `scripts/**`, and generated materialization outputs. It should distinguish at least three contexts: source package, materialized runtime, and generated ignored output. A path that is valid in `src/adapters/codex/**` may be invalid after materialization, and that is exactly the kind of drift this project must catch.

The graph validator should be conservative. Start by proving local Markdown links, required source paths, and runtime paths inside materialized outputs. Avoid a huge parser. Avoid trying to understand every code fence in the first pass. Make one useful cut, wire it into `npm run commit:check`, and record the document impact in TDS if the validation surface becomes a contract.

The second wave should be the first real behavioral eval runner. Today `scripts/context_mesh_plan.py` plans the ablation matrix, and that is useful, but it does not measure behavior. Build a runner that can consume `benchmarks/context-mesh/eval-dataset.json`, generate `full`, `none`, and `drop:<section>` conditions, preserve raw outputs, and produce a small report. The report must state model or tool mode, date, dataset version or hash, sample count, limitations, and whether the result is directional or blocking. Keep the first runner humble. The goal is measured learning, not a theatrical benchmark.

When that runner exists, TDS should receive an evidence path. Do not create a large evidence archive before there is evidence. The first useful shape is probably `docs/evidence/reports/**` for retained plain-language benchmark and materialization reports. Raw bundles can wait until there is a real L4 artifact with a restore story. TDS discipline means evidence is findable and honest, not heavy.

The third wave should certify the Claude adapter honestly. Local materialization currently proves file shape, plugin version, marketplace source, and skill paths. That is enough for source confidence, not enough for distribution certification. Find or define a Claude plugin installer oracle. If no reliable oracle is available, write a short adapter support statement that says Claude is source-aligned and locally materializable, while installer certification remains pending. Do not overclaim.

The fourth wave can consider materialization profiles only if a real target project needs them. The likely split is `codex-minimal`, which emits `AGENTS.md` plus `.agents/skills/**`, and `codex-full`, which may emit selected docs and validation scripts. Do not add profiles just because the materializer can support them. Add them when a consumer appears.

The fifth wave is packaging and release hygiene. Once graph validation, behavioral evals, TDS evidence, and Claude certification status are clear, the project can decide whether v0.1.0 is ready for a local release tag. Until then, keep it private, local, and precise. No remote, no marketplace publication, no public promise, and no inflated performance claim.

Preserve this honest measurement language: DUTT field use observed a major ambiguity reduction, and Murillo reported nearly 80 percent reduction in local practice. That is strong directional evidence, but it is not yet a formal package benchmark. The independent package earns formal claims only after the eval runner produces repeatable reports.

Use this operating order:

1. Seal the current staged architecture, TDS, and materialization patch.
2. Prove reentry with `npm run commit:check`.
3. Add reference graph validation.
4. Add the first behavioral eval runner.
5. Create retained TDS evidence only after real reports exist.
6. Certify or explicitly bound Claude packaging.
7. Add materialization profiles only for real consumers.

No-go conditions are simple. Do not reorganize `src/**` and `docs/**` again without a failing gate or a real consumer. Do not create empty documentation drawers. Do not let roadmap prose become source of truth. Do not claim three-tool certification until Claude has a real packaging oracle. Do not turn the reported 80 percent ambiguity reduction into a formal benchmark before the runner exists. Do not add `CHANGELOG.md`; use Git history.

The premium direction is this: keep the package small, measurable, and honest. Codex is the lead derivation. Cursor is the compact always-on guardrail. Claude is aligned but pending packaging proof. TDS is now installed to protect memory, not to decorate the repo. The next real leap is not more structure. The next real leap is measured behavior.
