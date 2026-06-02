---
tds_id: roadmap.tes_tts_cap_009_mixed_language_english_identity_hardening
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# TES TTS CAP-009 Mixed-Language And English Identity Hardening

## Purpose

Harden mixed-language spoken rendering so PT-BR platform narration preserves
English engineering, planning, product, package, model, command, and code
identity instead of translating protected terms into approximate Portuguese.

## Problem

CAP-008 made structured content speakable. The next quality risk was language
identity drift: terms such as `review`, `diff`, `worktree`, `GitHub Actions`,
`Node.js`, `Playwright`, `MCP server`, `LLM`, and `TTS` can sound awkward or
be misinterpreted when the surrounding narration is PT-BR or another platform
language.

CAP-009 keeps that identity dependency-free and instruction-level only. It
does not add a language detector, translator, G2P layer, SSML, IPA, lexicon,
phoneme output, or provider-backed pronunciation claim.

## Implementation Result

Status: `PASS` for the focused CAP-009 scope.

CAP-009 added fixture-backed English identity preservation:

- PT-BR narration keeps planning and review terms such as `review`, `diff`,
  `patch`, `worktree`, `sandbox`, `rollback`, and `release candidate`;
- mixed Spanish/PT-BR preparation keeps `backlog`, `roadmap`, `issue`,
  `milestone`, `sprint`, `hotfix`, `rebase`, `cherry-pick`, `fork`,
  `upstream`, `origin`, and `main`;
- product and platform names such as `GitHub Actions`, `Docker`,
  `Kubernetes`, `Node.js`, `TypeScript`, `Playwright`, and `MCP server` keep
  English pronunciation intent;
- Hebrew remains explicitly degraded while preserving protected English terms;
- CAP-008 structural oralization continues to preserve English identity.

The behavior was documented in the active workbench and mirrored into Codex
and Claude adapter skill sources.

## Acceptance Evidence

CAP-009 introduced these required fixtures:

| Fixture | Proves |
|---------|--------|
| `tts-cap009-ptbr-narration-english-workflow-identity` | PT-BR narration preserves common English workflow and CI/CD terms. |
| `tts-cap009-mixed-span-translation-degraded-preserves-english` | Mixed-language degraded translation planning keeps protected English planning terms. |
| `tts-cap009-product-package-model-identity` | Product, package, and model identities remain un-translated. |
| `tts-cap009-hebrew-degraded-keeps-english-identity` | Hebrew pronunciation remains degraded while English identities are preserved. |
| `tts-cap009-structural-rendering-keeps-english-identity` | Structural oralization from CAP-008 keeps protected English identity. |

## Boundaries Preserved

- No sync, release, push, tag, publish, provider install, provider download,
  provider certification, global config write, durable conversion cache,
  version bump, bundle generation, IPA, SSML, lexicon, G2P, model bundle, or
  runtime dependency import was performed.
- No proactive `speak` behavior entered `tes-tts`.
- Pronunciation remains instruction-level metadata only.
- User text is not summarized unless the user explicitly asks for summary.

## Next Prompt

Ready prompt:
Prompt artifact purged from tracked source on 2026-06-02
