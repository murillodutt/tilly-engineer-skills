---
tds_id: roadmap.tes_tts_skill_roadmap_history
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, and release reviewers
source_of_truth: false
evidence_level: L2
---

# TES TTS Roadmap History

This file compresses historical `tes-tts` evolution so the active roadmap can
stay objective and maintainable.

## Evolution Ledger

| Stage | Decision | Evidence |
|-------|----------|----------|
| 0 | Promote local read-aloud behavior into TES as a simple reactive skill. | `CONTRACT-HISTORY.md`; adapter `SKILL.md` files. |
| 1 | Keep `tes-tts` separate from proactive `speak`. | ADR 0004 non-goals; provider reference. |
| 2 | Absorb only portable `speak` lessons: provider order, fallback, errors, voice policy, and speech transformation. | `providers-and-fallbacks.md`. |
| 3 | Add default-language and pronunciation normalization as optional speech preparation. | `language-normalization.md`; ADR 0004. |
| 4 | Keep ADR 0004 as GPS/boundary, with pipeline detail in SPEC/audit records. | ADR 0004; normalization specs. |
| 5 | Treat provider libraries as optional candidates until local probes prove behavior. | Provider candidate review. |
| 6 | Add first-class language scope for `pt-BR`, `en`, `es`, `fr`, `it`, `de`, and `he`. | Architecture SPEC. |
| 7 | Define adapter default-language precedence. | Selector fixtures and language reference. |
| 8 | Require sequential convergence with tracked prompts while the line is non-converged. | Sequential Super SPEC. |
| 9 | Accept ADR 0004 as active boundary. | `TES-TTS-OWNER-001-ACCEPTANCE-DECISION.md`. |
| 10 | Move from governance-first to runtime-first execution. | `AGENTS.md`; RTE closure. |
| 11 | Pivot PT-BR pronunciation work toward lexical datasets and manifests. | LEX-001 through LEX-005. |
| 12 | Build a dependency-free runtime preparation path. | RTE-000 through RTE-006. |
| 13 | Add optional OmniVoice premium local provider after live quality evidence. | Commit `eb44ce7`; OmniVoice oracle. |

## Sequence Outcomes

| Sequence | Outcome | Notes |
|----------|---------|-------|
| Baseline TTS cycles | Completed enough for source delivery. | Release identity stayed separate. |
| TTS-010 through TTS-031 owner cycles | Historical/non-convergent. | Repeated no-decision loops are no longer productive unless a prompt contains an explicit owner decision. |
| Ten-SPEC convergence | Technically complete. | SPEC-009 and SPEC-010 deferred release identity pending owner decision. |
| OWNER-001 | ADR 0004 accepted. | Sync and release remained unauthorized. |
| CAP-001 through CAP-005 | Portable capability migration closed. | `speak` stayed a learning source, not copied behavior. |
| CAP-006 through CAP-009 | Conversational rendering and protected English identity improved. | CAP-010 superseded by lexical pivot. |
| LEX-001 through LEX-005 | PT-BR lexical evidence foundation closed. | Full dictionary vendoring and runtime IPA/SSML stayed forbidden. |
| RTE-000 through RTE-006 | Runtime-first latency and preparation path closed. | Runtime is dependency-free and measured separately from provider/playback. |
| OmniVoice product cut | Optional premium local provider added. | External env only; no redistribution or install claim. |

## Current Historical Lessons

- Markdown-shaped datasets do not scale; structured JSON/JSONL fixtures and
  manifests are the durable path.
- Provider pronunciation hacks were useful for discovery but are not enough
  for quality. Premium provider quality must be judged by generated audio.
- OmniVoice handled the real mixed PT-BR technical test far better than manual
  aliases with a Portuguese system voice.
- Runtime evidence matters more than new SPECs once the architecture is
  accepted.
- Long owner-decision loops should stop as soon as they stop producing product
  movement.

## Release Boundary History

The package has repeatedly kept release identity, sync, push, tag, publish,
provider install, provider download, and provider redistribution out of scope
unless explicitly authorized. That boundary remains active after the OmniVoice
cut: local optional provider evidence is not the same as public release
certification.
