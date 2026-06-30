# CANARY-REPAIR

Deterministic repair routes used (no manual lock/postinstall edits):

1. Removed OS residue (`.DS_Store`, etc.) from all three targets.
2. `install_mcp.py --helpers-only --overwrite` to refresh `.tes/bin/**` from package source.
3. `tes_install.py attach hooks --agent all` (positional surface) to refresh Codex hook absolute paths.
4. `tes_init.py --target --yes` to regenerate PROJECT-CONTEXT/REGISTER and runtime gates.
5. Claude mesh gap: copied `DOCUMENTATION-AUTHORITY.md` and contract YAML files from cursor canary (deterministic parity repair).
6. Git init + `.git/info/exclude` per SPEC-006.
7. `field_reports.py install-hook` for pre-push on all targets (status PASS).
8. Local pre-commit hook (oracles + `git diff --check`) per SPEC-007.
9. Updated Identity table Git HEAD in PROJECT-CONTEXT/PROJECT-REGISTER after baseline commit; amended baseline commits.
10. **Audit repair (codex):** removed 8 `.DS_Store` files; `tes_install install --attach all` + `postinstall` to recertify lock; doc fix in `INSTALLATION-FRAMEWORK.md` L79; baseline HEAD `cf84c93`.

Canary HEAD after repair:

| Canary | HEAD |
|--------|------|
| cursor | `c0c75da` |
| claude | `d9083a7` |
| codex | `cf84c93` |
