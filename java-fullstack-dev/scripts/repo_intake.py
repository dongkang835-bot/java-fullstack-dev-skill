#!/usr/bin/env python3
"""Read-only structure scan for a newly joined Java/full-stack workspace.

Prints file counts and candidate build/runtime versions. It never prints source
contents, configuration values, remote URLs, or environment variables.
"""

import argparse
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


SKIP_DIRS = {
    ".git", ".idea", ".vscode", ".next", ".cache", ".venv", "venv",
    "node_modules", "target", "dist", "build", "out", "coverage",
    "__pycache__", ".codex-worktrees", ".worktrees",
}
SOURCE_SUFFIXES = {".java", ".kt", ".vue", ".js", ".jsx", ".ts", ".tsx", ".xml", ".py"}
BUILD_NAMES = {"pom.xml", "build.gradle", "build.gradle.kts", "package.json", "mvnw", "gradlew"}
GUIDE_NAMES = {"AGENTS.md", "CLAUDE.md", "README.md", "INDEX.md", "ARCHITECTURE.md"}
JAVA_MARKERS = {
    "Controller": "@RestController",
    "Service": "@Service",
    "Transaction": "@Transactional",
    "Feign": "@FeignClient",
    "Permission": "@Secured",
    "Test": "@Test",
}


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix() or "."


def candidate_versions(path: Path) -> dict[str, str]:
    result = {}
    try:
        if path.name == "package.json":
            data = json.loads(path.read_text(encoding="utf-8"))
            engines = data.get("engines") or {}
            if isinstance(engines, dict) and isinstance(engines.get("node"), str):
                result["Node"] = engines["node"]
        elif path.name == "pom.xml":
            content = path.read_text(encoding="utf-8", errors="ignore")[:300000]
            for key, label in (("maven.compiler.source", "Java source"),
                               ("java.version", "Java version"),
                               ("spring-boot.version", "Spring Boot")):
                m = re.search(r"<" + re.escape(key) + r">\s*([^<\s]+)\s*</" + re.escape(key) + r">", content)
                if m and len(m.group(1)) < 50:
                    result[label] = m.group(1)
    except (OSError, ValueError, UnicodeError):
        pass
    return result


def git_baseline(path: Path) -> str:
    try:
        commit = subprocess.run(["git", "-C", str(path), "rev-parse", "--short", "HEAD"],
                                check=False, capture_output=True, text=True, timeout=5)
        branch = subprocess.run(["git", "-C", str(path), "rev-parse", "--abbrev-ref", "HEAD"],
                                check=False, capture_output=True, text=True, timeout=5)
        if commit.returncode == 0 and branch.returncode == 0:
            status = subprocess.run(["git", "-C", str(path), "status", "--porcelain", "-uno"],
                                    check=False, capture_output=True, text=True, timeout=5)
            worktree = "changed" if status.stdout.strip() else "clean"
            if status.returncode != 0:
                worktree = "unknown"
            return f"{branch.stdout.strip()} @ {commit.stdout.strip()} ({worktree})"
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "no local HEAD"


def scan(root: Path) -> dict:
    counts = Counter()
    groups = defaultdict(Counter)
    marker_files = Counter()
    build_files = []
    guides = []
    repos = []
    versions = []
    for base, dirs, files in os.walk(root, followlinks=False):
        base_path = Path(base)
        if base_path != root and ".git" in files + dirs:
            repos.append(rel(root, base_path))
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not (base_path / d).is_symlink()]
        for name in files:
            path = base_path / name
            if path.is_symlink():
                continue
            relative = path.relative_to(root)
            group = relative.parts[0] if len(relative.parts) > 1 else "(root)"
            suffix = path.suffix.lower()
            if suffix in SOURCE_SUFFIXES:
                counts[suffix] += 1
                groups[group][suffix] += 1
                if suffix == ".java":
                    try:
                        content = path.read_text(encoding="utf-8", errors="ignore")
                        for label, needle in JAVA_MARKERS.items():
                            if needle in content:
                                marker_files[label] += 1
                    except OSError:
                        pass
            if name in BUILD_NAMES:
                build_files.append(rel(root, path))
                if name in {"pom.xml", "package.json"} and len(relative.parts) <= 3:
                    hint = candidate_versions(path)
                    if hint:
                        versions.append((rel(root, path), hint))
            if name in GUIDE_NAMES and len(relative.parts) <= 3:
                guides.append(rel(root, path))
    return dict(counts=counts, groups=groups, markers=marker_files,
                builds=build_files, guides=guides, repos=repos, versions=versions)


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only Java/full-stack repository inventory")
    parser.add_argument("root", type=Path, help="workspace root; no files are changed")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        parser.error("root must be an existing directory")
    data = scan(root)
    print("# Repository intake (private output)")
    print("\nThis report contains local structure and should stay in the project's private workspace. Counts are approximate; markers are files containing annotation text, not verified behavior.\n")
    print("## Source files\n")
    for suffix, number in sorted(data["counts"].items(), key=lambda x: (-x[1], x[0])):
        print(f"- `{suffix}`: {number}")
    print("\n## Top-level areas\n")
    print("| Area | Java | Vue | JS/TS | XML | Python |")
    print("| --- | ---: | ---: | ---: | ---: | ---: |")
    for name, count in sorted(data["groups"].items()):
        if sum(count.values()) < 10:
            continue
        print(f"| `{name}` | {count['.java']} | {count['.vue']} | {sum(count[x] for x in ('.js','.jsx','.ts','.tsx'))} | {count['.xml']} | {count['.py']} |")
    print("\n## Java markers (approximate file counts)\n")
    for label, number in sorted(data["markers"].items()):
        print(f"- {label}: {number}")
    for title, items in (("Nested Git repositories", data["repos"]),
                         ("Build entry files", data["builds"]),
                         ("Project guide files", data["guides"])):
        print(f"\n## {title}\n")
        for item in sorted(items)[:80]:
            print(f"- `{item}`")
        if len(items) > 80:
            print(f"- … {len(items) - 80} more omitted")
    print("\n## Local Git baseline (no fetch performed)\n")
    print(f"- `(root)`: {git_baseline(root)}")
    for item in sorted(data["repos"])[:80]:
        print(f"- `{item}`: {git_baseline(root / item)}")
    print("\n## Version hints (verify against CI and team instructions)\n")
    for path, hint in sorted(data["versions"])[:50]:
        print(f"- `{path}`: " + ", ".join(f"{k}={v}" for k, v in hint.items()))
    if not data["versions"]:
        print("- None found at shallow build entry points")


if __name__ == "__main__":
    main()
