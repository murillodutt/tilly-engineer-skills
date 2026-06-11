#!/usr/bin/env python3
"""Plan and apply conservative project version bumps for TES targets."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SEMVER_RE = re.compile(r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?P<pre>-[0-9A-Za-z.-]+)?$")
VERSION_TOKEN_RE = re.compile(r"\b(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-[0-9A-Za-z.-]+)?\b")
EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    "tmp",
}
GLOBAL_CONFIG_ROOT = Path.home() / ".tes" / "bump"
LOCAL_CONFIG = Path(".tes/bump.json")
VERSION = "0.1.0"
VERSION_IDENTITY_GLOBS = (
    "VERSION",
    "package.json",
    "*/package.json",
    "**/package.json",
    "**/.claude-plugin/plugin.json",
    "**/.claude-plugin/marketplace.json",
    "**/.codex-plugin/plugin.json",
    "**/.codex-plugin/marketplace.json",
    "**/.agents/plugins/marketplace.json",
    "VERSION.md",
    "CLAUDE.md",
    "docs/dist/**",
    "index.json",
)
DELIVERED_BEHAVIOR_GLOBS = (
    "src/adapters/**",
    "docs/install/**",
    "docs/adapters/**",
    "docs/dist/**",
    "package.json",
    "bin/**",
    "scripts/tes_install.py",
    "scripts/tes_update.py",
    "scripts/tes_bundle.py",
    "scripts/materialize_adapter.py",
    "scripts/install_*.py",
    "scripts/cortex*.py",
    "scripts/field_reports*.py",
    "scripts/command_trigger_oracle.py",
    "scripts/platform_surface_oracle.py",
    "scripts/validate_reference_package.py",
)


class BumpError(RuntimeError):
    """User-facing bump failure."""


@dataclass(frozen=True)
class SourceVersion:
    path: Path
    kind: str
    version: str


@dataclass(frozen=True)
class Target:
    path: Path
    kind: str
    label: str
    pattern: str | None = None


@dataclass(frozen=True)
class TargetResult:
    target: Target
    status: str
    detail: str


def parse_semver(value: str) -> re.Match[str]:
    match = SEMVER_RE.match(value.strip())
    if not match:
        raise BumpError(f"invalid SemVer: {value!r}")
    return match


def compute_version(current: str, request: str | None) -> str:
    request = (request or "patch").strip()
    if request in {"", "patch"}:
        match = parse_semver(current)
        return f"{match['major']}.{match['minor']}.{int(match['patch']) + 1}"
    if request == "minor":
        match = parse_semver(current)
        return f"{match['major']}.{int(match['minor']) + 1}.0"
    if request == "major":
        match = parse_semver(current)
        return f"{int(match['major']) + 1}.0.0"
    parse_semver(request)
    return request


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BumpError(f"{path}: invalid JSON: {exc}") from exc


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temp_name = handle.name
    Path(temp_name).replace(path)


def write_json_atomic(path: Path, payload: Any) -> None:
    write_text_atomic(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)


def matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def git_output(root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def changed_paths(root: Path, staged_only: bool) -> list[str]:
    paths: set[str] = set()
    commands = [["diff", "--cached", "--name-only"]]
    if not staged_only:
        commands.append(["diff", "--name-only"])
        commands.append(["ls-files", "--others", "--exclude-standard"])
    for command in commands:
        for line in git_output(root, command).splitlines():
            line = line.strip()
            if line:
                paths.add(line)
    return sorted(paths)


def version_diff_detected(root: Path, relpath: str) -> bool:
    if relpath == "VERSION" or relpath.startswith("docs/dist/"):
        return True
    path = root / relpath
    if path.exists() and relpath in git_output(root, ["ls-files", "--others", "--exclude-standard"]).splitlines():
        return matches_any(relpath, VERSION_IDENTITY_GLOBS)

    diff = "\n".join(
        [
            git_output(root, ["diff", "--", relpath]),
            git_output(root, ["diff", "--cached", "--", relpath]),
        ]
    )
    if not diff:
        return False
    for line in diff.splitlines():
        if not line.startswith(("+", "-")) or line.startswith(("+++", "---")):
            continue
        lowered = line.lower()
        if '"version"' in lowered or "current version" in lowered or "> version:" in lowered:
            return True
        if relpath.endswith((".md", ".json")) and VERSION_TOKEN_RE.search(line):
            return True
    return False


def detect_source(root: Path) -> SourceVersion:
    version_file = root / "VERSION"
    if version_file.is_file():
        version = version_file.read_text(encoding="utf-8").strip()
        parse_semver(version)
        return SourceVersion(version_file, "version-file", version)

    package_json = root / "package.json"
    if package_json.is_file():
        data = load_json(package_json)
        version = data.get("version")
        if not isinstance(version, str):
            raise BumpError("package.json has no string version field")
        parse_semver(version)
        return SourceVersion(package_json, "package-json", version)

    raise BumpError("No version source found: expected VERSION or package.json")


def project_names(root: Path) -> list[str]:
    names = [root.name]
    package_json = root / "package.json"
    if package_json.is_file():
        try:
            data = load_json(package_json)
        except BumpError:
            data = {}
        name = data.get("name")
        if isinstance(name, str) and name and name not in names:
            names.append(name)
    return names


def package_name(root: Path) -> str | None:
    package_json = root / "package.json"
    if not package_json.is_file():
        return None
    try:
        data = load_json(package_json)
    except BumpError:
        return None
    name = data.get("name")
    return name if isinstance(name, str) else None


def is_tes_package_source(root: Path) -> bool:
    return (
        package_name(root) == "tilly-engineer-skills"
        and (root / "src/adapters").is_dir()
        and (root / "docs/dist").is_dir()
    )


def workspace_patterns(root: Path) -> list[str]:
    package_json = root / "package.json"
    if not package_json.is_file():
        return []
    data = load_json(package_json)
    workspaces = data.get("workspaces", [])
    if isinstance(workspaces, dict):
        workspaces = workspaces.get("packages", [])
    if not isinstance(workspaces, list):
        return []
    return [item for item in workspaces if isinstance(item, str)]


def discover_workspace_packages(root: Path) -> list[Path]:
    paths: set[Path] = set()
    patterns = workspace_patterns(root)
    if patterns:
        for pattern in patterns:
            for match in root.glob(pattern):
                package = match / "package.json" if match.is_dir() else match
                if package.name == "package.json" and package.is_file() and not is_excluded(package.relative_to(root)):
                    paths.add(package)
    else:
        for package in root.glob("*/package.json"):
            if not is_excluded(package.relative_to(root)):
                paths.add(package)
    return sorted(paths)


def glob_known_manifests(root: Path) -> list[Path]:
    patterns = (
        "**/.claude-plugin/plugin.json",
        "**/.claude-plugin/marketplace.json",
        "**/.codex-plugin/plugin.json",
        "**/.codex-plugin/marketplace.json",
        "**/.agents/plugins/marketplace.json",
    )
    paths: set[Path] = set()
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_file() and not is_excluded(path.relative_to(root)):
                paths.add(path)
    return sorted(paths)


def add_target(targets: dict[Path, Target], target: Target) -> None:
    targets.setdefault(target.path, target)


def discover_targets(root: Path) -> list[Target]:
    targets: dict[Path, Target] = {}

    version_file = root / "VERSION"
    if version_file.is_file():
        add_target(targets, Target(version_file, "version-file", "VERSION"))

    root_package = root / "package.json"
    if root_package.is_file():
        add_target(targets, Target(root_package, "json-version", "package.json"))

    for package in discover_workspace_packages(root):
        add_target(targets, Target(package, "json-version", str(package.relative_to(root))))

    for manifest in glob_known_manifests(root):
        rel = str(manifest.relative_to(root))
        if manifest.name == "marketplace.json":
            add_target(targets, Target(manifest, "marketplace-json", rel))
        else:
            add_target(targets, Target(manifest, "json-version", rel))

    version_md = root / "VERSION.md"
    if version_md.is_file():
        add_target(targets, Target(version_md, "regex", "VERSION.md", "**Current Version**: {{VERSION}}"))

    claude_md = root / "CLAUDE.md"
    if claude_md.is_file():
        add_target(targets, Target(claude_md, "regex", "CLAUDE.md", r"> Version: {{VERSION}}"))

    return sorted(targets.values(), key=lambda item: str(item.path))


def safe_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise BumpError(f"unsafe config path: {value}")
    return path


def load_custom_config(root: Path) -> tuple[Path | None, dict[str, Any] | None]:
    candidates = [root / LOCAL_CONFIG]
    for name in project_names(root):
        candidates.append(GLOBAL_CONFIG_ROOT / f"bump-{name}.json")
    for candidate in candidates:
        if candidate.is_file():
            config = load_json(candidate)
            if not isinstance(config, dict):
                raise BumpError(f"{candidate}: config must be a JSON object")
            return candidate, config
    return None, None


def custom_targets(root: Path, config: dict[str, Any]) -> list[Target]:
    targets = config.get("versionTargets", [])
    if not isinstance(targets, list):
        raise BumpError("config versionTargets must be an array")

    result: list[Target] = []
    for index, item in enumerate(targets, start=1):
        if not isinstance(item, dict):
            raise BumpError(f"config target #{index} must be an object")
        rel = item.get("path")
        kind = item.get("type")
        if not isinstance(rel, str):
            raise BumpError(f"config target #{index} missing string path")
        if kind not in {"json", "marketplace", "regex", "regex-all"}:
            raise BumpError(f"config target #{index} has unsupported type: {kind!r}")
        path = root / safe_relative_path(rel)
        if not path.is_file():
            raise BumpError(f"config target missing: {rel}")
        if kind == "json":
            result.append(Target(path, "json-version", rel))
            continue
        if kind == "marketplace":
            result.append(Target(path, "marketplace-json", rel))
            continue
        pattern = item.get("pattern")
        if not isinstance(pattern, str) or "{{VERSION}}" not in pattern:
            raise BumpError(f"config {kind} target #{index} needs pattern with {{VERSION}}")
        result.append(Target(path, "regex" if kind == "regex" else "regex-all", rel, pattern))
    return result


def merge_custom_targets(root: Path, discovered: list[Target]) -> tuple[list[Target], str | None]:
    config_path, config = load_custom_config(root)
    if config is None:
        return discovered, None

    expected = config.get("project")
    if isinstance(expected, str) and expected not in project_names(root):
        raise BumpError(
            f"{config_path}: project {expected!r} does not match detected names {', '.join(project_names(root))}"
        )

    # Key by (path, kind, pattern) rather than path alone, so one file can
    # carry several version occurrences with distinct patterns (e.g. a VERSION
    # constant plus an example ref in the same script). A config target that
    # exactly matches a discovered one still dedupes.
    def key(target: Target) -> tuple[str, str, str | None]:
        return (str(target.path), target.kind, target.pattern)

    targets = {key(target): target for target in discovered}
    for target in custom_targets(root, config):
        targets[key(target)] = target
    return (
        sorted(targets.values(), key=lambda item: (str(item.path), item.kind, item.pattern or "")),
        str(config_path),
    )


# Version sub-pattern for interpolation inside a template when matching ANY
# version. Unlike VERSION_TOKEN_RE it carries no leading/trailing \b, so the
# surrounding literal text in the user's pattern controls the boundary. With
# the \b present, a pattern like "v{{VERSION}}" expands to "v\b0\.3\.9" which
# never matches, because there is no word boundary between "v" and "0".
TEMPLATE_VERSION_PATTERN = r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-[0-9A-Za-z.-]+)?"


def regex_from_template(pattern: str, current: str | None = None) -> re.Pattern[str]:
    """Compile a {{VERSION}} template into a regex.

    When ``current`` is given, {{VERSION}} matches only that exact version
    (escaped) — so a bump never rewrites a neighbouring or historical version
    that happens to share the surrounding literal text. When ``current`` is
    None, {{VERSION}} matches any SemVer token (legacy/discovery behaviour).
    """
    escaped = re.escape(pattern)
    if current is not None:
        # Match the exact current version, but guard the right edge so "0.3.9"
        # does not match the "0.3.9" prefix of "0.3.99" (which would corrupt a
        # neighbouring version). Only a trailing digit, or a dot followed by a
        # digit, means a longer version token — a plain dot (e.g. "0.3.9.zip")
        # is fine and must still match.
        version_sub = re.escape(current) + r"(?!\d|\.\d)"
    else:
        version_sub = TEMPLATE_VERSION_PATTERN
    escaped = escaped.replace(re.escape("{{VERSION}}"), version_sub)
    return re.compile(escaped)


def update_target(target: Target, version: str, dry_run: bool, current: str | None = None) -> TargetResult:
    try:
        if target.kind == "version-file":
            old = target.path.read_text(encoding="utf-8").strip()
            parse_semver(old)
            if not dry_run:
                write_text_atomic(target.path, version + "\n")
            return TargetResult(target, "updated", f"{old} -> {version}")

        if target.kind == "json-version":
            data = load_json(target.path)
            if not isinstance(data, dict):
                raise BumpError("JSON root is not an object")
            old = data.get("version")
            if not isinstance(old, str):
                raise BumpError("missing string version field")
            parse_semver(old)
            data["version"] = version
            if not dry_run:
                write_json_atomic(target.path, data)
            return TargetResult(target, "updated", f"{old} -> {version}")

        if target.kind == "marketplace-json":
            data = load_json(target.path)
            changed = 0
            if isinstance(data, dict) and isinstance(data.get("plugins"), list):
                for plugin in data["plugins"]:
                    if isinstance(plugin, dict) and isinstance(plugin.get("version"), str):
                        parse_semver(plugin["version"])
                        plugin["version"] = version
                        changed += 1
            elif isinstance(data, dict) and isinstance(data.get("metadata"), dict):
                old = data["metadata"].get("version")
                if isinstance(old, str):
                    parse_semver(old)
                    data["metadata"]["version"] = version
                    changed += 1
            else:
                raise BumpError("marketplace JSON has no plugins[] or metadata.version")
            if changed == 0:
                raise BumpError("marketplace JSON has no versioned entries")
            if not dry_run:
                write_json_atomic(target.path, data)
            return TargetResult(target, "updated", f"{changed} version fields -> {version}")

        if target.kind == "regex":
            if not target.pattern:
                raise BumpError("missing regex pattern")
            text = target.path.read_text(encoding="utf-8")
            regex = regex_from_template(target.pattern, current)
            replacement = target.pattern.replace("{{VERSION}}", version)
            new_text, count = regex.subn(replacement, text, count=1)
            if count != 1:
                raise BumpError("pattern not found exactly once")
            if not dry_run:
                write_text_atomic(target.path, new_text)
            return TargetResult(target, "updated", f"pattern -> {version}")

        if target.kind == "regex-all":
            if not target.pattern:
                raise BumpError("missing regex pattern")
            text = target.path.read_text(encoding="utf-8")
            regex = regex_from_template(target.pattern, current)
            replacement = target.pattern.replace("{{VERSION}}", version)
            new_text, count = regex.subn(replacement, text)
            if count == 0:
                raise BumpError("pattern not found")
            if not dry_run:
                write_text_atomic(target.path, new_text)
            return TargetResult(target, "updated", f"{count} occurrences -> {version}")

        raise BumpError(f"unsupported target kind: {target.kind}")
    except Exception as exc:
        if isinstance(exc, BumpError):
            return TargetResult(target, "failed", str(exc))
        return TargetResult(target, "failed", repr(exc))


def validate_targets(targets: list[Target], version: str) -> list[TargetResult]:
    failures: list[TargetResult] = []
    for target in targets:
        result = verify_target(target, version)
        if result.status != "ok":
            failures.append(result)
    return failures


def verify_target(target: Target, version: str) -> TargetResult:
    try:
        if target.kind == "version-file":
            actual = target.path.read_text(encoding="utf-8").strip()
            return TargetResult(target, "ok" if actual == version else "failed", f"actual={actual}")
        if target.kind == "json-version":
            actual = load_json(target.path).get("version")
            return TargetResult(target, "ok" if actual == version else "failed", f"actual={actual}")
        if target.kind == "marketplace-json":
            data = load_json(target.path)
            versions: list[str] = []
            if isinstance(data, dict) and isinstance(data.get("plugins"), list):
                versions.extend(
                    plugin.get("version")
                    for plugin in data["plugins"]
                    if isinstance(plugin, dict) and isinstance(plugin.get("version"), str)
                )
            if isinstance(data, dict) and isinstance(data.get("metadata"), dict):
                actual = data["metadata"].get("version")
                if isinstance(actual, str):
                    versions.append(actual)
            ok = bool(versions) and all(item == version for item in versions)
            return TargetResult(target, "ok" if ok else "failed", f"actual={versions}")
        if target.kind == "regex":
            text = target.path.read_text(encoding="utf-8")
            expected = target.pattern.replace("{{VERSION}}", version) if target.pattern else version
            return TargetResult(target, "ok" if expected in text else "failed", f"expected={expected}")
        if target.kind == "regex-all":
            text = target.path.read_text(encoding="utf-8")
            if not target.pattern:
                return TargetResult(target, "failed", "missing regex pattern")
            # The bump matched only the current version, so other (historical)
            # versions are left intact by design. Synced simply means the new
            # version now appears in the pattern's surrounding context.
            expected = target.pattern.replace("{{VERSION}}", version)
            return TargetResult(target, "ok" if expected in text else "failed", f"expected={expected}")
        return TargetResult(target, "failed", f"unsupported kind={target.kind}")
    except Exception as exc:
        return TargetResult(target, "failed", repr(exc))


def plan(root: Path, request: str | None) -> dict[str, Any]:
    source = detect_source(root)
    targets, config_path = merge_custom_targets(root, discover_targets(root))
    if is_tes_package_source(root) and config_path is None:
        raise BumpError(
            "TES package source has release identity surfaces beyond generic discovery; "
            "create .tes/bump.json or use the package release workflow instead of a partial bump"
        )
    new_version = compute_version(source.version, request)
    if not targets:
        raise BumpError("No version targets discovered")
    return {
        "root": str(root),
        "source": str(source.path.relative_to(root)),
        "current_version": source.version,
        "new_version": new_version,
        "config": config_path,
        "targets": [
            {
                "path": str(target.path.relative_to(root)),
                "kind": target.kind,
                "label": target.label,
            }
            for target in targets
        ],
    }


def governance_check(root: Path, staged_only: bool) -> dict[str, Any]:
    paths = changed_paths(root, staged_only)
    version_paths = [
        path
        for path in paths
        if matches_any(path, VERSION_IDENTITY_GLOBS) and version_diff_detected(root, path)
    ]
    delivered_paths = [
        path
        for path in paths
        if matches_any(path, DELIVERED_BEHAVIOR_GLOBS)
    ]

    validation_failures: list[TargetResult] = []
    source: SourceVersion | None = None
    if version_paths:
        source = detect_source(root)
        targets, _config_path = merge_custom_targets(root, discover_targets(root))
        validation_failures = validate_targets(targets, source.version)

    if validation_failures:
        status = "NEEDS_REVIEW"
        reason = "version targets changed but discovered targets are not synchronized"
    elif delivered_paths and not version_paths:
        status = "NEEDS_VERSION_DECISION"
        reason = "delivered behavior changed without a detected version bump"
    elif version_paths:
        status = "PASS"
        reason = "version bump surfaces are synchronized"
    else:
        status = "PASS"
        reason = "no bump-triggering change detected"

    return {
        "status": status,
        "reason": reason,
        "scope": "staged" if staged_only else "working-tree",
        "source_version": source.version if source else None,
        "changed_paths": paths,
        "delivered_behavior_paths": delivered_paths,
        "version_change_paths": version_paths,
        "validation_failures": [
            {
                "path": str(item.target.path.relative_to(root)),
                "detail": item.detail,
            }
            for item in validation_failures
        ],
    }


def run(root: Path, request: str | None, dry_run: bool, yes: bool, json_output: bool) -> int:
    source = detect_source(root)
    targets, config_path = merge_custom_targets(root, discover_targets(root))
    if is_tes_package_source(root) and config_path is None:
        raise BumpError(
            "TES package source has release identity surfaces beyond generic discovery; "
            "create .tes/bump.json or use the package release workflow instead of a partial bump"
        )
    new_version = compute_version(source.version, request)

    if not yes and not dry_run:
        raise BumpError("Refusing to write without --yes. Re-run with --dry-run to inspect or --yes to apply.")

    source_target = next((target for target in targets if target.path == source.path), None)
    ordered = list(targets)
    if source_target:
        ordered = [source_target, *[target for target in targets if target.path != source.path]]

    results: list[TargetResult] = []
    for index, target in enumerate(ordered):
        result = update_target(target, new_version, dry_run, current=source.version)
        results.append(result)
        if index == 0 and result.status == "failed":
            break

    validation: list[TargetResult] = []
    if not dry_run and results and results[0].status != "failed":
        validation = validate_targets([result.target for result in results if result.status == "updated"], new_version)

    if json_output:
        print(json.dumps({
            "root": str(root),
            "current_version": source.version,
            "new_version": new_version,
            "dry_run": dry_run,
            "config": config_path,
            "results": [
                {"path": str(item.target.path.relative_to(root)), "status": item.status, "detail": item.detail}
                for item in results
            ],
            "validation_failures": [
                {"path": str(item.target.path.relative_to(root)), "detail": item.detail}
                for item in validation
            ],
        }, indent=2))
        return 1 if any(item.status == "failed" for item in results) or validation else 0

    verb = "Planned" if dry_run else "Version bumped"
    print(f"[+] {verb}: {source.version} -> {new_version}")
    print(f"[+] Source: {source.path.relative_to(root)}")
    if config_path:
        print(f"[+] Config: {config_path}")

    successes = [item for item in results if item.status == "updated"]
    failures = [item for item in results if item.status == "failed"]
    print(f"[+] Targets {'planned' if dry_run else 'updated'}: {len(successes)}")
    for item in successes:
        print(f"    - {item.target.path.relative_to(root)} ({item.detail})")
    for item in failures:
        print(f"[-] Failed: {item.target.path.relative_to(root)} - {item.detail}")

    if validation:
        print("[!] Self-validation failed:")
        for item in validation:
            print(f"    - {item.target.path.relative_to(root)} - {item.detail}")
    elif not dry_run and not failures:
        print("[+] Self-validation: all updated targets in sync")

    if not dry_run:
        changed_paths = " ".join(str(item.target.path.relative_to(root)) for item in successes)
        print("[i] Next steps:")
        print(f"    git add {changed_paths}")
        print(f'    git commit -m "chore(release): bump version to {new_version}"')

    return 1 if failures or validation else 0


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "VERSION").write_text("0.3.9\n", encoding="utf-8")
        write_json_atomic(root / "package.json", {"name": "fixture", "version": "0.3.9", "workspaces": ["packages/*"]})
        (root / "packages/a").mkdir(parents=True)
        write_json_atomic(root / "packages/a/package.json", {"name": "a", "version": "0.3.9"})
        (root / ".claude-plugin").mkdir()
        write_json_atomic(root / ".claude-plugin/plugin.json", {"name": "fixture", "version": "0.3.9"})
        write_json_atomic(root / ".claude-plugin/marketplace.json", {"plugins": [{"name": "fixture", "version": "0.3.9"}]})
        (root / "VERSION.md").write_text("**Current Version**: 0.3.9\n", encoding="utf-8")
        rc = run(root, "minor", dry_run=False, yes=True, json_output=True)
        if rc != 0:
            return rc
        failures = validate_targets(merge_custom_targets(root, discover_targets(root))[0], "0.4.0")
        if failures:
            for failure in failures:
                print(f"self-test failure: {failure.target.path}: {failure.detail}", file=sys.stderr)
            return 1

    # Custom config: regex-all (multi-occurrence) and marketplace (nested) targets.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_json_atomic(root / "package.json", {"name": "fixture", "version": "0.3.9"})
        # i18n-style surface: current version repeated on several lines, PLUS a
        # historical version (v0.3.99) that must survive the bump untouched.
        (root / "i18n.json").write_text(
            '{\n  "a": "install v0.3.9 now",\n  "b": "ref #v0.3.9",\n'
            '  "c": "again v0.3.9",\n  "zip": "skills-0.3.9.zip",\n'
            '  "hist": "changelog v0.3.99 stays"\n}\n',
            encoding="utf-8",
        )
        # marketplace with the version nested under plugins[].
        write_json_atomic(
            root / "marketplace.json",
            {"plugins": [{"name": "fixture", "version": "0.3.9"}]},
        )
        write_json_atomic(
            root / ".tes/bump.json",
            {
                "project": "fixture",
                "versionTargets": [
                    {"path": "i18n.json", "type": "regex-all", "pattern": "v{{VERSION}}"},
                    # Second pattern on the same file: a version followed by ".zip".
                    # Exercises (a) multiple targets per path and (b) the right-edge
                    # guard letting "0.3.9.zip" match while "0.3.99" does not.
                    {"path": "i18n.json", "type": "regex-all", "pattern": "{{VERSION}}.zip"},
                    {"path": "marketplace.json", "type": "marketplace"},
                ],
            },
        )
        rc = run(root, "minor", dry_run=False, yes=True, json_output=True)
        if rc != 0:
            print("self-test failure: custom-config bump returned nonzero", file=sys.stderr)
            return rc
        i18n_text = (root / "i18n.json").read_text(encoding="utf-8")
        if i18n_text.count("v0.4.0") != 3:
            print(f"self-test failure: regex-all did not replace all current-version occurrences: {i18n_text!r}", file=sys.stderr)
            return 1
        if "v0.3.99" not in i18n_text:
            print(f"self-test failure: regex-all corrupted a historical version: {i18n_text!r}", file=sys.stderr)
            return 1
        if "v0.3.9 " in i18n_text or '"v0.3.9"' in i18n_text:
            print(f"self-test failure: a current-version occurrence was left stale: {i18n_text!r}", file=sys.stderr)
            return 1
        if "0.4.0.zip" not in i18n_text:
            print(f"self-test failure: version before .zip not bumped (right-edge guard): {i18n_text!r}", file=sys.stderr)
            return 1
        market = load_json(root / "marketplace.json")
        if market["plugins"][0]["version"] != "0.4.0":
            print("self-test failure: marketplace nested version not bumped", file=sys.stderr)
            return 1
        # regex-all with a pattern that matches nothing must fail loudly.
        miss = update_target(Target(root / "i18n.json", "regex-all", "i18n.json", "zzz{{VERSION}}"), "0.5.0", dry_run=True, current="0.4.0")
        if miss.status != "failed":
            print("self-test failure: regex-all should fail when pattern is absent", file=sys.stderr)
            return 1

    for current, request, expected in (
        ("1.2.3", None, "1.2.4"),
        ("1.2.3", "patch", "1.2.4"),
        ("1.2.3", "minor", "1.3.0"),
        ("1.2.3", "major", "2.0.0"),
        ("1.2.3", "1.2.3-rc.1", "1.2.3-rc.1"),
    ):
        actual = compute_version(current, request)
        if actual != expected:
            print(f"self-test failure: {current} {request} -> {actual}, expected {expected}", file=sys.stderr)
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=False)
        write_json_atomic(root / "package.json", {"name": "fixture", "version": "0.1.0"})
        subprocess.run(["git", "config", "user.email", "tes@example.invalid"], cwd=root, text=True, capture_output=True, check=False)
        subprocess.run(["git", "config", "user.name", "TES Bump Self Test"], cwd=root, text=True, capture_output=True, check=False)
        subprocess.run(["git", "add", "package.json"], cwd=root, text=True, capture_output=True, check=False)
        subprocess.run(["git", "commit", "-m", "test: baseline"], cwd=root, text=True, capture_output=True, check=False)
        (root / "src/adapters/codex/skills/example").mkdir(parents=True)
        (root / "src/adapters/codex/skills/example/SKILL.md").write_text("# Example\n", encoding="utf-8")
        check = governance_check(root, staged_only=False)
        if check["status"] != "NEEDS_VERSION_DECISION":
            print(f"self-test failure: governance check returned {check['status']}", file=sys.stderr)
            return 1
    print("tes_bump.py self-test PASS")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plan and apply TES version bumps.")
    parser.add_argument("version_request", nargs="?", help="patch, minor, major, or explicit x.y.z[-pre]")
    parser.add_argument("--target", default=".", help="project root to bump")
    parser.add_argument("--dry-run", action="store_true", help="plan without writing")
    parser.add_argument("--governance-check", action="store_true", help="classify whether changed behavior needs a version decision")
    parser.add_argument("--staged", action="store_true", help="with --governance-check, inspect staged changes only")
    parser.add_argument("--yes", action="store_true", help="apply writes")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--self-test", action="store_true", help="run deterministic self-test")
    parser.add_argument("--version", dest="show_version", action="store_true", help="print helper contract version")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.show_version:
        print(VERSION)
        return 0
    if args.self_test:
        return self_test()

    root = Path(args.target).resolve()
    if not root.is_dir():
        print(f"[-] target is not a directory: {root}", file=sys.stderr)
        return 2

    try:
        if args.governance_check:
            result = governance_check(root, staged_only=args.staged)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"[+] Version governance: {result['status']}")
                print(f"[+] Reason: {result['reason']}")
                if result["source_version"]:
                    print(f"[+] Source version: {result['source_version']}")
                if result["delivered_behavior_paths"]:
                    print("[+] Delivered behavior paths:")
                    for path in result["delivered_behavior_paths"]:
                        print(f"    - {path}")
                if result["version_change_paths"]:
                    print("[+] Version change paths:")
                    for path in result["version_change_paths"]:
                        print(f"    - {path}")
                if result["validation_failures"]:
                    print("[!] Sync failures:")
                    for failure in result["validation_failures"]:
                        print(f"    - {failure['path']} - {failure['detail']}")
            return 0 if result["status"] == "PASS" else 1
        return run(root, args.version_request, dry_run=args.dry_run, yes=args.yes, json_output=args.json)
    except BumpError as exc:
        if args.json:
            print(json.dumps({"status": "BLOCKED", "error": str(exc)}, indent=2))
        else:
            print(f"[-] BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
