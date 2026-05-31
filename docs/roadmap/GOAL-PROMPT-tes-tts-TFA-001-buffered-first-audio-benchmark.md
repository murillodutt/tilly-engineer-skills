---
tds_id: roadmap.goal_prompt_tes_tts_tfa_001_buffered_first_audio_benchmark
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

/goal Continue TES TTS time-to-first-audio optimization.

Canonical artifact:
docs/roadmap/TES-TTS-SKILL-ROADMAP.md

Current unit:
TFA-001 Buffered First-Audio Benchmark

Certified context:
- `tes-tts` is reactive-only and uses direct local OmniVoice when configured.
- This prompt must be executable in a fresh Codex window without relying on
  chat history. Treat this file plus the re-read artifacts below as the full
  execution context.
- The human-rated long-read recipe keeps quality acceptable with direct
  resident `speak-long`, `quality`, `language en`, 420-char chunks, combined
  WAV, and 450 ms inter-chunk silence.
- Latest observed long read generated 3 chunks and started audible playback
  only after all chunks were synthesized and combined.
- Latest measured payload:
  - startup: about 3.8s;
  - first chunk synthesis: about 16.7s;
  - total synthesis: about 46.8s;
  - combined duration: about 74s;
  - text preparation: under 1 ms;
  - playback started after synthesis/combine, creating unacceptable perceived
    latency.
- Quality is acceptable for now; the target is execution latency, especially
  time-to-first-audio.
- Sync, release, push, tag, publish, provider install, provider download,
  provider certification, global config writes, durable conversion cache,
  committed audio/cache/model/venv, and proactive speak remain unauthorized.

New-window bootstrap:
- If `git status` shows pre-existing `AGENTS.md` drift, classify it as
  inherited/unrelated unless the current TFA unit explicitly needs it. Do not
  stage it.
- Active product route is direct/resident OmniVoice only. Server routes are
  legacy lab compatibility and must not be revived as the product path.
- Canonical local voice reference is
  `tmp/tes-tts-lab/omnivoice/refs/audio-modelo-clone-mono24k.wav`.
- Provider artifacts, generated WAV files, prompt caches, model files, and
  benchmark payloads stay under `tmp/**` and must not be committed.
- Use the benchmark text below for baseline and candidate runs unless a
  smaller deterministic dry-run fixture is needed for an oracle:

```text
Hoje vamos testar o TES-TTS em uma leitura longa, natural e técnica. Primeiro,
o sistema deve falar em português do Brasil, sem transformar este texto em
resumo. Depois, precisa preservar termos como ADR, API, SDK, CLI, MCP, JSON,
YAML, HTTP, Node.js, TypeScript, Python, OpenAI, GitHub Actions, Docker e
Kubernetes. Também deve tratar caminhos como `.agents/skills/tes-tts` apenas
como referência de pasta, e URLs como
`https://github.com/murillodutt/tilly-engineer-skills` como página do GitHub,
sem soletrar cada caractere. Em seguida, precisamos validar que comandos como
`rm -rf tmp` são lidos como texto e nunca executados. Se aparecer um segredo,
por exemplo `API_KEY=abc123SECRET`, ele deve ser ocultado antes da fala. O
objetivo deste teste é perceber ritmo, pausas, pronúncia de termos em inglês,
estabilidade da voz clonada, cortes entre blocos e clareza geral. Por fim, o
áudio gerado deve permitir escuta repetida, comparação entre versões e
avaliação humana objetiva, sem depender de uma explicação paralela no chat.
```

Baseline command shape:

```bash
python3 scripts/tes_tts_omnivoice_provider.py speak-long \
  --text "$TFA_TEXT" \
  --output-dir "tmp/tes-tts-omnivoice-provider/tfa-001-baseline/<run-id>" \
  --latency-profile quality \
  --language en \
  --text-mode redacted_source \
  --chunk-chars 420 \
  --combine \
  --inter-chunk-silence-ms 450
```

Candidate command shape:

```bash
python3 scripts/tes_tts_omnivoice_provider.py speak-long \
  --text "$TFA_TEXT" \
  --output-dir "tmp/tes-tts-omnivoice-provider/tfa-001-candidate/<run-id>" \
  --latency-profile quality \
  --language en \
  --text-mode redacted_source \
  --chunk-chars 420 \
  --combine \
  --inter-chunk-silence-ms 450 \
  <new first-audio or buffered-playback flags added by this unit>
```

Task:
Execute only TFA-001 through:
execute -> analyze -> fix -> certify -> benchmark -> close or create exact
defect prompt -> local commit.

Central rule:
Optimize perceived start latency without reducing the accepted quality recipe.
Do not create a follow-up prompt by habit. Create one only if benchmark evidence
shows a specific remaining implementation defect that cannot be fixed in
TFA-001.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited changes. Do not stage or modify unrelated drift such as
   `AGENTS.md` unless it is explicitly part of this unit.
3. Re-read:
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/TES-TTS-RUNTIME-PYTHON-OPTIMIZATION-AUDIT.md`
   - `.agents/skills/tes-tts/SKILL.md`
   - `scripts/tes_tts_omnivoice_provider.py`
   - `scripts/tes_tts_omnivoice_runtime_support.py`
   - `scripts/tes_tts_omnivoice_direct_kernel.py`
   - `scripts/tes_tts_omnivoice_provider_oracle.py`
4. Implement TFA-001 only:
   - add a benchmarked first-audio strategy for long reads;
   - preserve the existing quality profile and provider defaults;
   - support an initial microchunk plus buffered playback plan, or an
     equivalent implementation that can reduce time-to-first-audio;
   - avoid uncomfortable gaps by requiring a buffer policy before continuous
     playback starts;
   - preserve existing combined-WAV output for repeat listening and review;
   - keep source text immutable, request-local speech, redaction, exact
     islands, code no-execute posture, no-summary behavior, and provider
     absence degradation.
5. Benchmark evidence must include:
   - baseline command and result for current combined-only behavior;
   - candidate command and result for first-audio/buffered behavior;
   - `time_to_first_audio_ms` or a deterministic proxy if direct playback
     timing cannot be measured safely;
   - startup, first chunk synthesis, total synthesis, combine time, playback
     time, chunk count, chunk durations, and gap/buffer status;
   - generated WAV paths under `tmp/**` only when audio is generated;
   - no committed audio or cache.
6. Acceptance targets:
   - no quality-profile downgrade from `quality`;
   - no provider install/download/global write;
   - no secret leak or source mutation;
   - first audible output should begin before full synthesis completes;
   - target `time_to_first_audio_ms` improvement is at least 40% versus the
     combined-only baseline, or else stop as `PERFORMANCE_REGRESSION` with
     evidence;
   - buffered playback must not introduce known uncomfortable gaps. If gaps
     are detected or cannot be bounded, keep the feature behind an opt-in flag
     and report `DEGRADED`.
7. Analyze the diff for latency truthfulness, quality preservation, buffer
   continuity, false-green risk, privacy, runtime hot-path cost, and line
   fidelity.
8. Fix only observed TFA-001 defects.
9. Certify with the smallest relevant set:
   - `python3 -m compileall -q scripts/tes_tts_omnivoice_provider.py scripts/tes_tts_omnivoice_runtime_support.py scripts/tes_tts_omnivoice_direct_kernel.py scripts/tes_tts_omnivoice_provider_oracle.py`
   - `python3 scripts/tes_tts_omnivoice_provider_oracle.py --self-test`
   - focused dry-run or runtime benchmark commands changed by this unit;
   - `python3 scripts/tes_tts_runtime_latency_oracle.py --self-test`
   - `python3 scripts/materialize_adapter.py all --check`
   - `python3 scripts/tes_tts_roadmap_partition_oracle.py`
   - `python3 scripts/validate_tds.py`
   - `git diff --check`
   - `git diff --cached --check`
10. Close the TFA line if benchmark targets pass and no immediate defect
    remains. Create the next exact `/goal` prompt only for a measured defect
    that cannot be fixed inside TFA-001.
11. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with outcome, benchmark
    pointer, closure state or next prompt pointer, and sync status.
12. Stage only TFA-001 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, runtime dependency
  import, full dictionary vendoring, committed audio, committed cache,
  committed model artifact, committed venv, command execution from spoken
  content, user-text summary without explicit request, obsolete route
  resurrection, server route resurrection as product path, or unrelated
  `.agents/**` / `AGENTS.md` changes without explicit current-cycle approval.

Stop states:
PASS, DEGRADED, PERFORMANCE_REGRESSION, QUALITY_REGRESSION, TTS_NOT_AVAILABLE,
NEEDS_REVIEW, SAFETY_BLOCKED, BLOCKED.

Required closeout:
- changed files;
- baseline versus candidate benchmark result;
- first-audio/buffer outcome;
- focused oracles and result;
- local comparison WAV paths when generated, explicitly under `tmp/**`;
- next prompt artifact only if a measured defect remains, otherwise closure
  statement;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
