---
tds_id: evidence.context_mesh.project_context_real_canaries_2026_05_08
tds_class: evidence
status: active
consumer: installer authors, context-oracle maintainers, and certification reviewers
source_of_truth: false
evidence_level: L3
---

# Project Context Real Canary Loop - 2026-05-08

## Scope

Validate `/tes-init` as a useful project-start ritual, not only a TES runtime
installer. Canaries were disposable local sandboxes under
`/Users/murillo/Dev/tes-canaries/**`; no canary repository was committed or
pushed.

## Canaries

| Canary | Project shape | Result |
|---|---|---|
| `pypa/sampleproject` | Python package with `pyproject.toml`, `src`, tests, GitHub workflows | PASS |
| `sindresorhus/ky` | TypeScript package, lowercase `readme.md`, sponsor HTML before tagline | PASS |
| `pallets/click` | Python package with docs, examples, `src`, tests, Python tool config | PASS |
| `hashicorp-education/learn-terraform-import` | Terraform tutorial/config with `##` README heading and HCL fences | PASS |
| `expressjs/express` | Node package with classic `package.json` scripts | PASS |
| `sampleproject` with local bootloaders | Project-owned `AGENTS.md`, `CLAUDE.md`, Cursor rule | PASS |

## Bugs Found And Converted

| Finding | Evidence from canary | Product fix | Regression gate |
|---|---|---|---|
| Installed `field_reports.py` crashed copying itself onto `.tes/bin/field_reports.py` | `SameFileError` during `/tes-init` in Ky, Click, Terraform, and sampleproject sandboxes | `copy_helper()` skips self-copy when helper is already installed | `scripts/field_reports.py --self-test` installed-helper fixture |
| Partial bootstrap context looked official | Failed init left `PROJECT-CONTEXT.md` with `bootstrap: true`, `file_count=0`; `tes_update.py plan` still said CURRENT | `project_context_oracle.py` fails bootstrap-only context; `tes_update.py` includes `project_context_status` and routes to `/tes-init` on drift | `project_context_oracle.py --self-test`, `tes_update.py --self-test` |
| TES runtime internals polluted project anchors | First green canary listed `.tes/bin/**` in Source Anchors and Recommended Deep Reads | `tes_init.py` excludes `.tes/**` from project inventory while preserving runtime surface reporting | `tes_init.py --self-test`; real canary rerun verified `.tes/bin` absent from anchors/deep reads |
| README extraction was too shallow | Ky initially risked sponsor HTML instead of product tagline; Terraform chose `docker_container.web:` from fenced HCL as identity | README parser skips leading HTML, accepts blockquote taglines, supports lowercase `readme.md`, accepts `#`/`##`/`###` headings outside fenced code | `tes_init.py --self-test`, `project_context_oracle.py --self-test`, Ky and Terraform canaries |
| Python identity and gates were weak | Click and sampleproject needed `pyproject.toml` name/description and Python gates | `tes_init.py` and oracle parse `pyproject.toml`; quality scripts detect `nox`, `tox`, `pytest`, `ruff`, `mypy`, `pyright`, `sphinx` | `tes_init.py --self-test`, `project_context_oracle.py --self-test`, Click/sampleproject canaries |
| Terraform root files were not anchors | Terraform canary only cited README | `.tf`, `.tfvars`, and `.hcl` root files are first-class anchors | `tes_init.py --self-test`, `project_context_oracle.py --self-test`, `install_smoke.py --self-test` fixture |
| Project-owned bootloaders needed preservation proof | Local `AGENTS.md`, `CLAUDE.md`, and Cursor rule must survive adapter install | Existing preserved-conflict path was canary-tested with non-conflicting TES-owned skill/rule installation | Real bootloader canary; `install_smoke.py --self-test` preserved bootloader probes |

## Final Canary Snapshot

| Canary | `/tes-init` | `project_context_oracle.py --target` | `tes_update.py plan` | Notable checks |
|---|---:|---:|---:|---|
| sampleproject | PASS, 12 files | PASS | CURRENT, scope `none` | `sampleproject`, `pyproject.toml`, `src`, tests, `nox` |
| Ky | PASS, 67 files | PASS | CURRENT, scope `none` | lowercase `readme.md`, package description, TypeScript source/test territories |
| Click | PASS, 149 files | PASS | CURRENT, scope `none` | docs/examples/src/tests, `pytest`, `ruff`, `mypy`, `pyright`, `sphinx`, `tox` |
| Terraform import | PASS, 7 files | PASS | CURRENT, scope `none` | `Learn Terraform Import`, README prose, `main.tf` anchor |
| Express | PASS, 213 files | PASS | CURRENT, scope `none` | `express`, package description, Node scripts |
| Owned bootloaders | PASS, 15 files | PASS | CURRENT, scope `none` | local bootloaders preserved, TES Cursor rule present |

## Maintainer Gates Run

```text
python3 scripts/field_reports.py --self-test
python3 scripts/tes_init.py --self-test
python3 scripts/project_context_oracle.py --self-test
python3 scripts/tes_update.py --self-test
python3 scripts/install_smoke.py --self-test
```

All listed gates passed before this report was written.

## Residual Risk

The deterministic scaffold is now materially useful across diverse repositories,
but it is not a semantic analyst by itself. The generated context explicitly
requires the active agent to open strong anchors before claiming deep project
understanding in non-trivial projects.
