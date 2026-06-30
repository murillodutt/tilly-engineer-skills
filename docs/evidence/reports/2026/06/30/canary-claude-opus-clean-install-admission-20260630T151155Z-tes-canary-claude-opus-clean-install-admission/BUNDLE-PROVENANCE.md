---
tds_id: evidence.canary_claude_opus_clean_install_admission_aborted.bundle_provenance_20260630
tds_class: evidence
status: archived
consumer: maintainers, canary operators, and Goal Maestro operators
source_of_truth: false
evidence_level: L1
---

# BUNDLE-PROVENANCE.md

SPEC-001 — Prove The Prepared Local Bundle
Captured: 2026-06-30T15:13:57Z
Executor: Claude Code / Claude Opus 4.8 Max

## File existence
```
OK /Users/murillo/Dev/tilly-engineer-skills/docs/dist/0.3.231/tilly-engineer-skills-0.3.231.zip
OK /Users/murillo/Dev/tilly-engineer-skills/docs/dist/0.3.231/tilly-engineer-skills-0.3.231.zip.sha256
```

## shasum -a 256 (live)
```
565ccb30abceb635056db9f7211f155a740a2a7163895a52900304cc2c2a1912  /Users/murillo/Dev/tilly-engineer-skills/docs/dist/0.3.231/tilly-engineer-skills-0.3.231.zip
```

## sha256 sidecar
```
565ccb30abceb635056db9f7211f155a740a2a7163895a52900304cc2c2a1912  tilly-engineer-skills-0.3.231.zip
```

## Expected SHA: 565ccb30abceb635056db9f7211f155a740a2a7163895a52900304cc2c2a1912
## Match: YES

## index.json
```json
{
  "version": "0.3.231",
  "sha256": "565ccb30abceb635056db9f7211f155a740a2a7163895a52900304cc2c2a1912",
  "source_commit": "7a664a93b54575e99348cba216728da895b080c0",
  "metadata": {
    "created_at": "2026-06-30T11:24:20-03:00",
    "schema": "tes-bundle-metadata@1",
    "source_branch": "main",
    "source_commit": "7a664a93b54575e99348cba216728da895b080c0",
    "source_ref": "HEAD",
    "source_repository": "https://github.com/murillodutt/tilly-engineer-skills.git",
    "source_tree_state": "clean",
    "version": "0.3.231"
  },
  "stage_dir": ".tes/setup/0.3.231"
}
```

## ZIP manifest summary (tes-bundle-manifest.json)
```json
{
  "version": "0.3.231",
  "source_commit": "7a664a93b54575e99348cba216728da895b080c0",
  "entry_count": 378,
  "pycache": 0
}
```

## Self-tests
```
tes_bundle.py --self-test  -> EXIT 0 status PASS (self_test_mode source-package)
tes_install.py --self-test -> EXIT 0 status PASS [tes-install:self-test] PASS
install_smoke.py --self-test -> EXIT 0 status PASS (28 routes all PASS)
```

## Acceptance verdict
- ZIP SHA equals expected: YES
- index.json points to same SHA: YES
- ZIP manifest has no __pycache__/.pyc: YES (pycache=0)
- Bundle/installer/smoke self-tests pass: YES (all exit 0)
- Bundle source_commit: 7a664a93b54575e99348cba216728da895b080c0 (matches index.json)
- Note: ZIP manifest entry_count=378 (bundle payload). Installed manifests show 379 (adds a target-generated entry). SPEC-001 fixes no exact count; pycache=0 and SHA match are the gates.
