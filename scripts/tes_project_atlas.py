#!/usr/bin/env python3
"""Build and render the TES adaptive Project Atlas."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any


VERSION = "0.3.176"
SCRIPT_PATH = Path(__file__).resolve()
PACKAGE_MODE = (SCRIPT_PATH.parents[1] / "package.json").exists() and SCRIPT_PATH.parent.name == "scripts"
GPS_DIR_REL = Path(".tes/gps")
VIEW_FILES = {
    "project_overview": "project-overview.eraserdiagram",
    "module_tree": "module-tree.eraserdiagram",
    "dependency_map": "dependency-map.eraserdiagram",
    "data_map": "data-map.eraserdiagram",
    "runtime_integrations": "runtime-integrations.eraserdiagram",
    "gates_evidence": "gates-evidence.eraserdiagram",
    "project_gps": "project-gps.eraserdiagram",
}
EXCLUDED_PARTS = {
    ".git",
    ".hg",
    ".svn",
    ".tes",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".next",
    ".nuxt",
    "dist",
    "build",
    "coverage",
}
SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs"}
DATA_SUFFIXES = {".sql", ".prisma"}
MANIFEST_NAMES = {
    "package.json",
    "pyproject.toml",
    "go.mod",
    "Cargo.toml",
    "pnpm-workspace.yaml",
    "Makefile",
    "GNUmakefile",
    "docker-compose.yml",
    "docker-compose.yaml",
}
QUALITY_TERMS = ("ci", "doc", "fmt", "gen", "lint", "typecheck", "test", "spec", "check", "build", "contract", "validate")
DB_DEPENDENCY_HINTS = {
    "drizzle-orm",
    "prisma",
    "@prisma/client",
    "typeorm",
    "sequelize",
    "knex",
    "sqlalchemy",
    "django",
    "psycopg",
    "psycopg2",
    "asyncpg",
    "pg",
    "mysql2",
    "sqlite3",
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def read_toml(path: Path) -> dict[str, Any]:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def is_excluded(path: Path, target: Path) -> bool:
    try:
        relpath = path.relative_to(target)
    except ValueError:
        return True
    return any(part in EXCLUDED_PARTS for part in relpath.parts)


def git_files(target: Path) -> list[Path] | None:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=target,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return [target / raw.decode("utf-8") for raw in result.stdout.split(b"\0") if raw]


def iter_project_files(target: Path) -> list[Path]:
    from_git = git_files(target)
    if from_git:
        return sorted(path for path in from_git if path.is_file() and not is_excluded(path, target))
    return sorted(path for path in target.rglob("*") if path.is_file() and not is_excluded(path, target))


def git_value(target: Path, args: list[str]) -> str | None:
    result = subprocess.run(["git", *args], cwd=target, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def clean_label(value: str, fallback: str = "unknown", max_len: int = 64) -> str:
    label = re.sub(r"\s+", " ", str(value or "").strip()) or fallback
    label = label.replace('"', "'").replace("[", "(").replace("]", ")")
    if len(label) > max_len:
        label = label[: max_len - 1].rstrip() + "..."
    return label


def node_id(kind: str, value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_]+", "_", value.strip().lower()).strip("_")
    if not slug:
        slug = "unknown"
    if slug[0].isdigit():
        slug = f"n_{slug}"
    return f"{kind}_{slug[:54]}"


def eraser_node(identifier: str, label: str, *, shape: str = "rectangle", color: str = "gray", icon: str | None = None) -> str:
    props = [f'label: "{clean_label(label)}"', f"shape: {shape}", f"color: {color}"]
    if icon:
        props.append(f"icon: {icon}")
    return f"{identifier} [{', '.join(props)}]"


def add_node(nodes: dict[str, dict[str, Any]], kind: str, label: str, **attrs: Any) -> str:
    identifier = attrs.pop("id", node_id(kind, label))
    nodes.setdefault(identifier, {"id": identifier, "kind": kind, "label": clean_label(label), **attrs})
    return identifier


def add_edge(edges: list[dict[str, str]], source: str, target: str, relation: str, evidence: str = "") -> None:
    edge = {"source": source, "target": target, "relation": relation, "evidence": evidence}
    if edge not in edges:
        edges.append(edge)


def package_dependencies(target: Path) -> tuple[list[dict[str, str]], dict[str, str]]:
    package = read_json(target / "package.json")
    deps: list[dict[str, str]] = []
    for field in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        values = package.get(field)
        if isinstance(values, dict):
            for name, version in sorted(values.items()):
                deps.append({"name": str(name), "version": str(version), "source": f"package.json:{field}", "ecosystem": "node"})
    scripts = package.get("scripts")
    script_map = {str(k): str(v) for k, v in sorted(scripts.items())} if isinstance(scripts, dict) else {}
    return deps, script_map


def python_dependencies(target: Path) -> list[dict[str, str]]:
    pyproject = read_toml(target / "pyproject.toml")
    project = pyproject.get("project") if isinstance(pyproject.get("project"), dict) else {}
    deps: list[dict[str, str]] = []
    for value in project.get("dependencies", []) if isinstance(project.get("dependencies"), list) else []:
        deps.append({"name": re.split(r"[<>=\[\] ;]", str(value), maxsplit=1)[0], "version": str(value), "source": "pyproject.toml:project.dependencies", "ecosystem": "python"})
    optional = project.get("optional-dependencies")
    if isinstance(optional, dict):
        for group, values in optional.items():
            if isinstance(values, list):
                for value in values:
                    deps.append({"name": re.split(r"[<>=\[\] ;]", str(value), maxsplit=1)[0], "version": str(value), "source": f"pyproject.toml:optional.{group}", "ecosystem": "python"})
    return deps


def go_dependencies(target: Path) -> list[dict[str, str]]:
    text = read_text(target / "go.mod")
    deps: list[dict[str, str]] = []
    in_require = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("require ("):
            in_require = True
            continue
        if in_require and stripped == ")":
            in_require = False
            continue
        if stripped.startswith("require "):
            stripped = stripped.removeprefix("require ").strip()
        elif not in_require:
            continue
        parts = stripped.split()
        if len(parts) >= 2 and not parts[0].startswith("//"):
            deps.append({"name": parts[0], "version": parts[1], "source": "go.mod:require", "ecosystem": "go"})
    return deps


def rust_dependencies(target: Path) -> list[dict[str, str]]:
    cargo = read_toml(target / "Cargo.toml")
    deps: list[dict[str, str]] = []
    for section in ("dependencies", "dev-dependencies", "build-dependencies"):
        values = cargo.get(section)
        if isinstance(values, dict):
            for name, value in sorted(values.items()):
                deps.append({"name": str(name), "version": cargo_dep_version(value), "source": f"Cargo.toml:{section}", "ecosystem": "rust"})
    workspace = cargo.get("workspace") if isinstance(cargo.get("workspace"), dict) else {}
    workspace_deps = workspace.get("dependencies")
    if isinstance(workspace_deps, dict):
        for name, value in sorted(workspace_deps.items()):
            deps.append({"name": str(name), "version": cargo_dep_version(value), "source": "Cargo.toml:workspace.dependencies", "ecosystem": "rust"})
    return deps


def cargo_dep_version(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return str(value.get("version") or value.get("path") or value.get("workspace") or "declared")
    return "declared"


def terraform_dependencies(target: Path) -> list[dict[str, str]]:
    deps: list[dict[str, str]] = []
    for path in sorted(target.glob("*.tf")):
        text = read_text(path)
        for match in re.finditer(r'source\s*=\s*"(?P<source>[^"]+)"', text):
            source = match.group("source")
            if source.startswith("hashicorp/") or "/" in source:
                deps.append({"name": source, "version": "declared", "source": rel(path, target), "ecosystem": "terraform"})
    return deps[:24]


def workspace_patterns(target: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    package = read_json(target / "package.json")
    workspaces = package.get("workspaces")
    patterns = workspaces.get("packages") if isinstance(workspaces, dict) else workspaces
    if isinstance(patterns, list):
        records.extend({"source": "package.json", "kind": "npm workspace", "pattern": str(item)} for item in patterns)
    pnpm = read_text(target / "pnpm-workspace.yaml")
    in_packages = False
    for line in pnpm.splitlines():
        stripped = line.strip()
        if stripped.startswith("packages:"):
            in_packages = True
            continue
        if in_packages and stripped.startswith("- "):
            records.append({"source": "pnpm-workspace.yaml", "kind": "pnpm workspace", "pattern": stripped[2:].strip("'\"")})
        elif in_packages and stripped and not line.startswith((" ", "\t")):
            break
    cargo = read_toml(target / "Cargo.toml")
    workspace = cargo.get("workspace") if isinstance(cargo.get("workspace"), dict) else {}
    members = workspace.get("members")
    if isinstance(members, list):
        records.extend({"source": "Cargo.toml", "kind": "cargo workspace", "pattern": str(item)} for item in members)
    return records


def infer_stack(target: Path, deps: list[dict[str, str]], files: list[Path]) -> list[str]:
    names = {item["name"] for item in deps}
    stacks: list[str] = []
    checks = (
        ((target / "package.json").exists(), "node"),
        (any(name in names for name in {"typescript", "tsx", "vite", "next", "nuxt", "react", "vue"}), "typescript/web"),
        ((target / "pyproject.toml").exists(), "python"),
        ((target / "go.mod").exists(), "go"),
        ((target / "Cargo.toml").exists(), "rust"),
        (any(path.suffix == ".tf" for path in files), "terraform"),
        (any(path.name in {"Dockerfile", "docker-compose.yml", "docker-compose.yaml"} for path in files), "ops/docker"),
        (any(".github/workflows/" in rel(path, target) for path in files), "ci/github-actions"),
        (any(name in names for name in DB_DEPENDENCY_HINTS) or any("/migrations/" in f"/{rel(path, target)}" for path in files), "data/db"),
        ((target / "docs").exists(), "docs"),
    )
    for present, label in checks:
        if present:
            stacks.append(label)
    return sorted(dict.fromkeys(stacks))


def import_edges(target: Path, files: list[Path], module_ids: dict[str, str], limit: int = 120) -> list[dict[str, str]]:
    roots = sorted(module_ids)
    edges: list[dict[str, str]] = []
    source_files = [path for path in files if path.suffix in SOURCE_SUFFIXES][:limit]
    patterns = (
        re.compile(r"^\s*import\s+(?:.+?\s+from\s+)?['\"](?P<name>[^'\"]+)['\"]"),
        re.compile(r"^\s*from\s+(?P<name>[A-Za-z0-9_.]+)\s+import\s+"),
        re.compile(r"^\s*import\s+(?P<name>[A-Za-z0-9_.]+)"),
        re.compile(r"^\s*use\s+(?P<name>[A-Za-z0-9_:]+)"),
    )
    for path in source_files:
        source_rel = rel(path, target)
        source_root = source_rel.split("/", 1)[0]
        source_id = module_ids.get(source_root)
        if not source_id:
            continue
        for line in read_text(path).splitlines()[:160]:
            for pattern in patterns:
                match = pattern.match(line)
                if not match:
                    continue
                raw = match.group("name")
                candidate = raw.split("/", 1)[0].split(".", 1)[0].split("::", 1)[0]
                target_id = module_ids.get(candidate)
                if target_id and target_id != source_id:
                    edge = {"source": source_id, "target": target_id, "relation": "imports", "evidence": source_rel}
                    if edge not in edges:
                        edges.append(edge)
                break
    return edges[:60]


def build_atlas(target: Path, *, gps_model: dict[str, Any] | None = None, deep: bool = False) -> dict[str, Any]:
    target = target.resolve()
    files = iter_project_files(target)
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []
    package_deps, scripts = package_dependencies(target)
    deps = [*package_deps, *python_dependencies(target), *go_dependencies(target), *rust_dependencies(target), *terraform_dependencies(target)]
    stacks = infer_stack(target, deps, files)
    git_head = git_value(target, ["rev-parse", "--short=12", "HEAD"]) or "unknown"
    package = read_json(target / "package.json")
    pyproject = read_toml(target / "pyproject.toml")
    project = pyproject.get("project") if isinstance(pyproject.get("project"), dict) else {}
    name = str(project.get("name") or package.get("name") or target.name)
    description = str(project.get("description") or package.get("description") or "source-derived project atlas")

    project_id = add_node(nodes, "project", name, description=description, git_head=git_head, stacks=stacks)
    suffixes = Counter(path.suffix or "[none]" for path in files)
    top_level = Counter(rel(path, target).split("/", 1)[0] for path in files if "/" in rel(path, target))
    module_ids: dict[str, str] = {}
    for name_part, count in sorted(top_level.items(), key=lambda item: (-item[1], item[0]))[:16]:
        role = territory_role(name_part, [rel(path, target) for path in files if rel(path, target).startswith(f"{name_part}/")])
        territory_id = add_node(nodes, "territory", name_part, file_count=count, role=role)
        add_edge(edges, project_id, territory_id, "contains", "top-level file inventory")
        if name_part in {"src", "app", "server", "client", "api", "lib", "packages", "internal", "crates", "docs", "tests", "scripts"}:
            module_ids[name_part] = add_node(nodes, "module", name_part, role=role, file_count=count)
            add_edge(edges, territory_id, module_ids[name_part], "contains", "source territory")

    for dep in deps[:80]:
        dep_id = add_node(nodes, "dependency", dep["name"], ecosystem=dep["ecosystem"], source=dep["source"])
        add_edge(edges, project_id, dep_id, "depends_on", dep["source"])
    for workspace in workspace_patterns(target)[:24]:
        ws_id = add_node(nodes, "workspace", workspace["pattern"], source=workspace["source"], workspace_kind=workspace["kind"])
        add_edge(edges, project_id, ws_id, "contains", workspace["source"])

    for data in data_surfaces(target, files, deps):
        data_id = add_node(nodes, "data_surface", data["label"], source=data["source"], evidence=data["evidence"], weak=data.get("weak", False))
        add_edge(edges, project_id, data_id, "reads", data["evidence"])
        add_edge(edges, data_id, project_id, "writes", data["evidence"])
    for runtime in runtime_surfaces(target, files):
        runtime_id = add_node(nodes, "runtime_surface", runtime["label"], source=runtime["source"], weak=runtime.get("weak", False))
        add_edge(edges, project_id, runtime_id, "belongs_to", runtime["source"])
    for name_script, command in scripts.items():
        if any(term in name_script.lower() for term in QUALITY_TERMS):
            gate_id = add_node(nodes, "gate", name_script, command=command)
            add_edge(edges, gate_id, project_id, "validates", "package.json scripts")
    for evidence in evidence_nodes(target, files):
        evidence_id = add_node(nodes, "evidence", evidence["label"], source=evidence["source"])
        add_edge(edges, evidence_id, project_id, "proves", evidence["source"])
    for risk in risk_nodes(target, files, deps):
        risk_id = add_node(nodes, "risk", risk["label"], evidence=risk["evidence"], weak=risk.get("weak", False))
        add_edge(edges, risk_id, project_id, "blocks", risk["evidence"])
    unknown_label = "No unresolved unknowns recorded"
    if gps_model and gps_model.get("unknowns"):
        unknown_label = str(gps_model["unknowns"][0])
    unknown_id = add_node(nodes, "unknown", unknown_label)
    add_edge(edges, project_id, unknown_id, "contains", "gps unknowns")
    if gps_model:
        gps_id = add_node(nodes, "gps_position", str(gps_model.get("position") or "Project GPS"), status=str(gps_model.get("status") or "unknown"))
        add_edge(edges, project_id, gps_id, "next_step", str(gps_model.get("next_safe_move") or "unknown"))
    if deep:
        for edge in import_edges(target, files, module_ids):
            add_edge(edges, edge["source"], edge["target"], edge["relation"], edge["evidence"])

    summary = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "stacks": stacks,
        "file_count": len(files),
        "top_level": dict(sorted(top_level.items())),
        "suffixes": dict(sorted(suffixes.items())),
        "deep": deep,
        "confidence": "high" if files and (deps or top_level) else "medium" if files else "low",
    }
    return {"version": VERSION, "schema": "tes-project-atlas@1", "target": str(target), "summary": summary, "nodes": list(nodes.values()), "edges": edges}


def territory_role(name: str, paths: list[str]) -> str:
    lowered = name.lower()
    if lowered in {"docs", "doc", "api-docs"}:
        return "documentation and contract surface"
    if lowered in {"src", "app", "server", "client", "api", "lib", "packages", "internal", "crates"}:
        return "product/source module territory"
    if lowered in {"drizzle", "prisma", "migrations", "migration"} or any("/migrations/" in path for path in paths):
        return "database schema and migration territory"
    if lowered in {"tests", "test", "spec"}:
        return "verification territory"
    if lowered in {"scripts", "tools", "bin"}:
        return "developer automation and oracle territory"
    if lowered in {"infra", "infrastructure", "ops", ".github"}:
        return "operations and delivery territory"
    return "project territory to inspect"


def data_surfaces(target: Path, files: list[Path], deps: list[dict[str, str]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for dep in deps:
        if dep["name"] in DB_DEPENDENCY_HINTS:
            records.append({"label": dep["name"], "source": "dependency", "evidence": dep["source"]})
    for path in files:
        path_rel = rel(path, target)
        lowered = path_rel.lower()
        if path.suffix in DATA_SUFFIXES or "migration" in lowered or "schema" in lowered and path.suffix in {".ts", ".py", ".sql", ".prisma"}:
            records.append({"label": path_rel, "source": "file", "evidence": path_rel, "weak": "fixture" in lowered or "example" in lowered})
    return records[:32]


def runtime_surfaces(target: Path, files: list[Path]) -> list[dict[str, Any]]:
    checks = (
        ("Dockerfile", "Docker runtime", "Dockerfile"),
        ("docker-compose.yml", "Docker Compose services", "docker-compose.yml"),
        ("docker-compose.yaml", "Docker Compose services", "docker-compose.yaml"),
        (".github/workflows", "GitHub Actions workflows", ".github/workflows"),
        ("Makefile", "Make targets", "Makefile"),
        ("go.mod", "Go module", "go.mod"),
        ("Cargo.toml", "Cargo package/workspace", "Cargo.toml"),
        ("pyproject.toml", "Python package", "pyproject.toml"),
    )
    records: list[dict[str, Any]] = []
    rels = {rel(path, target) for path in files}
    for needle, label, source in checks:
        if any(path == needle or path.startswith(f"{needle}/") for path in rels):
            records.append({"label": label, "source": source})
    if any(path.endswith(".tf") for path in rels):
        records.append({"label": "Terraform infrastructure", "source": "*.tf"})
    docs_files = [path for path in rels if path.startswith("docs/")]
    if docs_files:
        records.append({"label": "Documentation contract surface", "source": "docs/**", "weak": True})
    return records


def evidence_nodes(target: Path, files: list[Path]) -> list[dict[str, str]]:
    records = [{"label": "git HEAD", "source": git_value(target, ["rev-parse", "--short=12", "HEAD"]) or "git unavailable"}]
    for relpath in ("README.md", "readme.md", "package.json", "pyproject.toml", "go.mod", "Cargo.toml"):
        if (target / relpath).exists():
            records.append({"label": relpath, "source": relpath})
    records.extend({"label": rel(path, target), "source": rel(path, target)} for path in files if rel(path, target).startswith("docs/agents/evidence/"))
    return records[:12]


def risk_nodes(target: Path, files: list[Path], deps: list[dict[str, str]]) -> list[dict[str, Any]]:
    rels = [rel(path, target) for path in files]
    risks: list[dict[str, Any]] = []
    if any("/migrations/" in f"/{path}" for path in rels):
        risks.append({"label": "Migration/schema history requires project workflow", "evidence": "migrations", "weak": False})
    if any(path in {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Cargo.lock", "uv.lock", "poetry.lock"} for path in rels):
        risks.append({"label": "Dependency lockfile changes require package-manager workflow", "evidence": "lockfile", "weak": False})
    if any(path.startswith("docs/") for path in rels):
        risks.append({"label": "Docs are weak runtime evidence until source anchors confirm claims", "evidence": "docs/**", "weak": True})
    if not deps and not any(path in MANIFEST_NAMES for path in rels):
        risks.append({"label": "No package manifest detected; architecture confidence limited", "evidence": "manifest scan", "weak": True})
    return risks


def nodes_by_kind(atlas: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    return [node for node in atlas["nodes"] if node.get("kind") == kind]


def render_header() -> list[str]:
    return ["flow-chart", "direction right", "styleMode plain", "typeface clean", "colorMode pastel", ""]


def render_view(atlas: dict[str, Any], view: str, gps_model: dict[str, Any] | None = None) -> str:
    renderers = {
        "project_overview": render_project_overview,
        "module_tree": render_module_tree,
        "dependency_map": render_dependency_map,
        "data_map": render_data_map,
        "runtime_integrations": render_runtime_integrations,
        "gates_evidence": render_gates_evidence,
        "project_gps": lambda a: render_project_gps(a, gps_model or {}),
    }
    return renderers[view](atlas)


def render_project_overview(atlas: dict[str, Any]) -> str:
    project = nodes_by_kind(atlas, "project")[0]
    lines = render_header()
    lines.extend([
        eraser_node("project", project["label"], shape="oval", color="blue", icon="box"),
        eraser_node("territories", f"{len(nodes_by_kind(atlas, 'territory'))} territories", color="indigo", icon="folder"),
        eraser_node("modules", f"{len(nodes_by_kind(atlas, 'module'))} modules", color="green", icon="code"),
        eraser_node("deps", f"{len(nodes_by_kind(atlas, 'dependency'))} dependencies", color="purple", icon="package"),
        eraser_node("data", f"{len(nodes_by_kind(atlas, 'data_surface'))} data surfaces", shape="cylinder", color="orange", icon="database"),
        eraser_node("gates", f"{len(nodes_by_kind(atlas, 'gate'))} gates", shape="diamond", color="teal", icon="check-circle"),
        eraser_node("risks", f"{len(nodes_by_kind(atlas, 'risk'))} risks", color="red", icon="alert-triangle"),
        "project > territories, modules, deps, data, gates, risks",
        legend(),
    ])
    return "\n".join(lines).rstrip() + "\n"


def render_module_tree(atlas: dict[str, Any]) -> str:
    lines = render_header()
    lines.append(eraser_node("project", nodes_by_kind(atlas, "project")[0]["label"], shape="oval", color="blue", icon="box"))
    for node in nodes_by_kind(atlas, "territory")[:14]:
        nid = node["id"]
        lines.append(eraser_node(nid, f"{node['label']} ({node.get('file_count', '?')})", color="indigo", icon="folder"))
        lines.append(f"project > {nid}: contains")
    for node in nodes_by_kind(atlas, "module")[:12]:
        nid = node["id"]
        lines.append(eraser_node(nid, node["label"], color="green", icon="code"))
        lines.append(f"project > {nid}: module")
    for edge in [edge for edge in atlas["edges"] if edge["relation"] == "imports"][:24]:
        lines.append(f"{edge['source']} --> {edge['target']}: imports [color: green]")
    lines.append(legend())
    return "\n".join(lines).rstrip() + "\n"


def render_dependency_map(atlas: dict[str, Any]) -> str:
    lines = render_header()
    lines.append(eraser_node("project", nodes_by_kind(atlas, "project")[0]["label"], shape="oval", color="blue", icon="box"))
    for node in nodes_by_kind(atlas, "workspace")[:12]:
        lines.append(eraser_node(node["id"], node["label"], color="indigo", icon="layers"))
        lines.append(f"project > {node['id']}: workspace")
    for node in nodes_by_kind(atlas, "dependency")[:32]:
        color = "orange" if node["label"] in DB_DEPENDENCY_HINTS else "purple"
        lines.append(eraser_node(node["id"], node["label"], color=color, icon="package"))
        lines.append(f"project --> {node['id']}: depends_on")
    lines.append(legend())
    return "\n".join(lines).rstrip() + "\n"


def render_data_map(atlas: dict[str, Any]) -> str:
    lines = render_header()
    lines.append(eraser_node("project", nodes_by_kind(atlas, "project")[0]["label"], shape="oval", color="blue", icon="box"))
    data = nodes_by_kind(atlas, "data_surface")
    if not data:
        lines.append(eraser_node("no_data", "No explicit data surface detected", shape="cylinder", color="gray", icon="database"))
        lines.append("project -- no_data: not detected")
    for node in data[:32]:
        color = "yellow" if node.get("weak") else "orange"
        lines.append(eraser_node(node["id"], node["label"], shape="cylinder", color=color, icon="database"))
        lines.append(f"project > {node['id']}: reads/writes")
    lines.append(legend())
    return "\n".join(lines).rstrip() + "\n"


def render_runtime_integrations(atlas: dict[str, Any]) -> str:
    lines = render_header()
    lines.append(eraser_node("project", nodes_by_kind(atlas, "project")[0]["label"], shape="oval", color="blue", icon="box"))
    for node in nodes_by_kind(atlas, "runtime_surface")[:24]:
        color = "yellow" if node.get("weak") else "teal"
        lines.append(eraser_node(node["id"], node["label"], color=color, icon="terminal"))
        lines.append(f"project > {node['id']}: runtime")
    lines.append(legend())
    return "\n".join(lines).rstrip() + "\n"


def render_gates_evidence(atlas: dict[str, Any]) -> str:
    lines = render_header()
    lines.append(eraser_node("project", nodes_by_kind(atlas, "project")[0]["label"], shape="oval", color="blue", icon="box"))
    for node in nodes_by_kind(atlas, "gate")[:20]:
        lines.append(eraser_node(node["id"], node["label"], shape="diamond", color="teal", icon="check-circle"))
        lines.append(f"{node['id']} > project: validates")
    for node in nodes_by_kind(atlas, "evidence")[:12]:
        lines.append(eraser_node(node["id"], node["label"], shape="document", color="green", icon="file-text"))
        lines.append(f"{node['id']} > project: proves")
    for node in nodes_by_kind(atlas, "risk")[:10]:
        lines.append(eraser_node(node["id"], node["label"], color="red", icon="alert-triangle"))
        lines.append(f"{node['id']} --> project: blocks")
    lines.append(legend())
    return "\n".join(lines).rstrip() + "\n"


def render_project_gps(atlas: dict[str, Any], gps_model: dict[str, Any]) -> str:
    position = clean_label(gps_model.get("position") or "Project GPS position")
    next_step = clean_label(gps_model.get("next_safe_move") or gps_model.get("next_irreversible_step") or "Next safe move")
    proof = clean_label(gps_model.get("proof_gate") or "proof gate")
    blocked = clean_label((gps_model.get("blocking_items") or ["No blocker recorded"])[0])
    unknown = clean_label((gps_model.get("unknowns") or ["No unknown recorded"])[0])
    lines = render_header()
    lines.extend([
        eraser_node("done", "Done evidence", color="green", icon="check"),
        eraser_node("current", f"You are here: {position}", color="blue", icon="navigation"),
        eraser_node("next", f"Next: {next_step}", color="orange", icon="arrow-right"),
        eraser_node("proof", f"Proof: {proof}", shape="diamond", color="teal", icon="shield-check"),
        eraser_node("blocked", f"Blocked: {blocked}", color="red", icon="alert-triangle"),
        eraser_node("unknown", f"Unknown: {unknown}", color="gray", icon="help-circle"),
        "done > current > next > proof",
        "current --> blocked: blocked_by [color: red]",
        "current --> unknown: unknown [color: gray]",
        legend(),
    ])
    return "\n".join(lines).rstrip() + "\n"


def legend() -> str:
    return """legend [position: bottom-left] {
  [color: blue, label: Project/current]
  [color: green, label: Source/evidence]
  [color: orange, label: Data/next]
  [color: red, label: Risk/blocker]
  [connection: -->, label: Inferred or weak]
}"""


def write_views(target: Path, atlas: dict[str, Any], *, gps_model: dict[str, Any] | None = None) -> dict[str, Any]:
    out_dir = target / GPS_DIR_REL
    out_dir.mkdir(parents=True, exist_ok=True)
    views: dict[str, dict[str, Any]] = {}
    changed = False
    for view, filename in VIEW_FILES.items():
        path = out_dir / filename
        text = render_view(atlas, view, gps_model)
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old != text:
            path.write_text(text, encoding="utf-8")
            changed = True
        views[view] = {"path": rel(path, target), "changed": old != text}
    index_path = out_dir / "atlas.json"
    payload = json.dumps(atlas, indent=2, sort_keys=True) + "\n"
    old_index = index_path.read_text(encoding="utf-8") if index_path.exists() else None
    if old_index != payload:
        index_path.write_text(payload, encoding="utf-8")
        changed = True
    return {"changed": changed, "atlas": rel(index_path, target), "views": views}


def write_fixture(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def atlas_fixture_cases(root: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    node = root / "node-typescript-app"
    write_fixture(node / "README.md", "# Node TypeScript App\n")
    write_fixture(node / "package.json", json.dumps({
        "name": "node-typescript-app",
        "dependencies": {"@prisma/client": "^5.0.0", "typescript": "^5.0.0", "vite": "^5.0.0"},
        "scripts": {"test": "vitest run", "lint": "eslint .", "typecheck": "tsc --noEmit"},
    }))
    write_fixture(node / "src/app.ts", "import './db'\n")
    write_fixture(node / "src/db.ts", "export const db = {}\n")
    write_fixture(node / "prisma/schema.prisma", "model User { id Int @id }\n")
    cases.append({"name": "node-typescript-app", "path": node, "stacks": {"node", "typescript/web", "data/db"}, "kinds": {"project", "module", "dependency", "data_surface", "gate"}})

    python = root / "python-package"
    write_fixture(python / "README.md", "# Python Package\n")
    write_fixture(python / "pyproject.toml", "[project]\nname = \"python-package\"\ndescription = \"python fixture\"\ndependencies = [\"sqlalchemy>=2\"]\n")
    write_fixture(python / "src/python_package/__init__.py", "from .repo import load\n")
    write_fixture(python / "src/python_package/repo.py", "import sqlalchemy\n\ndef load():\n    return None\n")
    write_fixture(python / "tests/test_repo.py", "from python_package import load\n")
    cases.append({"name": "python-package", "path": python, "stacks": {"python", "data/db"}, "kinds": {"project", "module", "dependency", "data_surface", "runtime_surface"}})

    go = root / "go-module"
    write_fixture(go / "README.md", "# Go Module\n")
    write_fixture(go / "go.mod", "module example.com/go-module\n\ngo 1.22\n\nrequire github.com/lib/pq v1.10.9\n")
    write_fixture(go / "internal/store/store.go", "package store\n")
    cases.append({"name": "go-module", "path": go, "stacks": {"go"}, "kinds": {"project", "territory", "dependency", "runtime_surface"}})

    rust = root / "rust-workspace"
    write_fixture(rust / "README.md", "# Rust Workspace\n")
    write_fixture(rust / "Cargo.toml", "[workspace]\nmembers = [\"crates/core\", \"crates/cli\"]\n\n[workspace.dependencies]\nserde = \"1\"\n")
    write_fixture(rust / "crates/core/src/lib.rs", "pub fn value() -> u8 { 1 }\n")
    write_fixture(rust / "crates/cli/src/main.rs", "fn main() {}\n")
    cases.append({"name": "rust-workspace", "path": rust, "stacks": {"rust"}, "kinds": {"project", "territory", "dependency", "workspace", "runtime_surface"}})

    terraform = root / "terraform-infra"
    write_fixture(terraform / "README.md", "# Terraform Infra\n")
    write_fixture(terraform / "main.tf", 'terraform {\n  required_providers {\n    aws = { source = "hashicorp/aws" }\n  }\n}\nmodule "network" { source = "./modules/network" }\n')
    write_fixture(terraform / "modules/network/main.tf", "resource \"aws_vpc\" \"main\" {}\n")
    cases.append({"name": "terraform-infra", "path": terraform, "stacks": {"terraform"}, "kinds": {"project", "territory", "dependency", "runtime_surface"}})

    db = root / "db-migrations-repo"
    write_fixture(db / "README.md", "# DB Migrations\n")
    write_fixture(db / "migrations/001_init.sql", "create table account(id int primary key);\n")
    write_fixture(db / "schema.prisma", "model Account { id Int @id }\n")
    cases.append({"name": "db-migrations-repo", "path": db, "stacks": {"data/db"}, "kinds": {"project", "territory", "data_surface", "risk"}})

    docs = root / "docs-heavy-repo"
    write_fixture(docs / "README.md", "# Docs Heavy Repo\n")
    write_fixture(docs / "docs/api.md", "# API Contract\n")
    write_fixture(docs / "docs/manual.md", "# Manual\n")
    cases.append({"name": "docs-heavy-repo", "path": docs, "stacks": {"docs"}, "kinds": {"project", "territory", "runtime_surface", "risk"}, "weak_required": True})

    mixed = root / "mixed-monorepo"
    write_fixture(mixed / "README.md", "# Mixed Monorepo\n")
    write_fixture(mixed / "package.json", json.dumps({
        "name": "mixed-monorepo",
        "workspaces": ["packages/*", "apps/*"],
        "dependencies": {"typescript": "^5.0.0", "drizzle-orm": "^1.0.0"},
        "scripts": {"test": "node test.js", "lint": "eslint ."},
    }))
    write_fixture(mixed / "pnpm-workspace.yaml", "packages:\n  - 'packages/*'\n  - 'apps/*'\n")
    write_fixture(mixed / "Makefile", "test:\n\tnode test.js\n")
    write_fixture(mixed / "src/index.ts", "import 'packages/core'\n")
    write_fixture(mixed / "packages/core/src/index.ts", "export const core = true\n")
    write_fixture(mixed / "apps/web/src/main.ts", "export const app = true\n")
    write_fixture(mixed / "migrations/001.sql", "create table mixed(id int);\n")
    cases.append({"name": "mixed-monorepo", "path": mixed, "stacks": {"node", "typescript/web", "data/db"}, "kinds": {"project", "module", "workspace", "dependency", "data_surface", "gate"}, "relations": {"imports"}})

    return cases


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-atlas-self-test-") as tmp:
        root = Path(tmp)
        fixture_results: list[dict[str, Any]] = []
        gps_model = {"position": "Atlas adoption", "next_safe_move": "Retest", "proof_gate": "self-test", "unknowns": ["Fixture unknown"]}
        for case in atlas_fixture_cases(root):
            atlas = build_atlas(case["path"], gps_model=gps_model, deep=True)
            kinds = {node["kind"] for node in atlas["nodes"]}
            stacks = set(atlas["summary"]["stacks"])
            relations = {edge["relation"] for edge in atlas["edges"]}
            missing_kinds = sorted(case["kinds"] - kinds)
            missing_stacks = sorted(case["stacks"] - stacks)
            missing_relations = sorted(case.get("relations", set()) - relations)
            for kind in missing_kinds:
                failures.append(f"{case['name']}: missing node kind: {kind}")
            for stack in missing_stacks:
                failures.append(f"{case['name']}: missing stack: {stack}")
            for relation in missing_relations:
                failures.append(f"{case['name']}: missing relation: {relation}")
            if case.get("weak_required") and not any(node.get("weak") for node in atlas["nodes"] if node["kind"] in {"runtime_surface", "risk", "data_surface"}):
                failures.append(f"{case['name']}: missing weak evidence label")
            for relation in ("contains", "proves"):
                if relation not in relations:
                    failures.append(f"{case['name']}: missing base relation: {relation}")
            fixture_results.append({"name": case["name"], "node_count": len(atlas["nodes"]), "edge_count": len(atlas["edges"]), "stacks": atlas["summary"]["stacks"]})

        target = root / "mixed-monorepo"
        atlas = build_atlas(target, gps_model=gps_model, deep=True)
        relations = {edge["relation"] for edge in atlas["edges"]}
        for relation in ("contains", "depends_on", "imports", "reads", "writes", "validates", "proves", "blocks", "belongs_to", "next_step"):
            if relation not in relations:
                failures.append(f"mixed-monorepo: missing relation: {relation}")
        written = write_views(target, atlas, gps_model=gps_model)
        second = write_views(target, atlas, gps_model=gps_model)
        if not written["changed"]:
            failures.append("first write did not create atlas views")
        if second["changed"]:
            failures.append("second write was not idempotent")
        for filename in VIEW_FILES.values():
            path = target / GPS_DIR_REL / filename
            if not path.exists() or not path.read_text(encoding="utf-8").startswith("flow-chart\n"):
                failures.append(f"invalid Eraser sidecar: {filename}")
    return {
        "status": "FAIL" if failures else "PASS",
        "version": VERSION,
        "self_test_mode": "package" if PACKAGE_MODE else "installed",
        "coverage": "source-package-contract" if PACKAGE_MODE else "installed-helper-contract",
        "fixtures": fixture_results,
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the TES adaptive Project Atlas.")
    parser.add_argument("--target", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--deep", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        result = self_test()
    else:
        target = Path(args.target).resolve()
        atlas = build_atlas(target, deep=args.deep)
        write = write_views(target, atlas) if args.write else None
        result = {"status": "PASS", "version": VERSION, "atlas": atlas, "write": write}
    print(json.dumps(result, indent=2, sort_keys=True) if args.json or args.self_test else result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
