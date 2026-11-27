#!/usr/bin/env python3
"""Freeze a local Git review scope without fetching or changing the repository.

Output is private: file and branch names may reveal project information.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def git_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in (
        "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
        "GIT_NAMESPACE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_REPLACE_REF_BASE",
    ):
        env.pop(key, None)
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    return env


def run_git(repo: Path, *args: str, allow_failure: bool = False) -> bytes:
    proc = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo), *args],
        capture_output=True, env=git_env(), timeout=20, check=False,
    )
    if proc.returncode and not allow_failure:
        message = proc.stderr.decode("utf-8", errors="replace").strip().splitlines()
        raise ValueError(message[-1] if message else f"git exited {proc.returncode}")
    return proc.stdout


def decoded(data: bytes) -> str:
    return data.decode("utf-8", errors="replace").strip()


def sha(repo: Path, ref: str) -> str:
    if not ref.strip():
        raise ValueError("revision cannot be blank")
    return decoded(run_git(repo, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"))


def path_list(data: bytes) -> list[str]:
    return sorted({part.decode("utf-8", errors="replace") for part in data.split(b"\0") if part})


def scope(args: argparse.Namespace) -> dict:
    requested = args.repo.expanduser().resolve()
    if not requested.is_dir():
        raise ValueError("--repo must be an existing directory")
    repo = Path(decoded(run_git(requested, "rev-parse", "--show-toplevel"))).resolve()
    branch = decoded(run_git(repo, "symbolic-ref", "--short", "HEAD", allow_failure=True)) or "detached"
    result = {"repository": str(repo), "branch": branch, "mode": "", "requested_base_sha": None,
              "diff_base_sha": None, "target_sha": None, "paths": [], "staged": [],
              "unstaged": [], "untracked": [], "comparison": None}

    if args.worktree:
        result["mode"] = "worktree"
        result["comparison"] = "HEAD plus staged, unstaged and untracked"
        result["diff_base_sha"] = result["target_sha"] = sha(repo, "HEAD")
        result["staged"] = path_list(run_git(repo, "diff", "--cached", "--name-only", "-z", "HEAD", "--"))
        result["unstaged"] = path_list(run_git(repo, "diff", "--name-only", "-z", "--"))
        result["untracked"] = path_list(run_git(repo, "ls-files", "--others", "--exclude-standard", "-z"))
        result["paths"] = sorted(set(result["staged"] + result["unstaged"] + result["untracked"]))
    elif args.commit:
        target = sha(repo, args.commit)
        parents = decoded(run_git(repo, "rev-list", "--parents", "-n", "1", target)).split()
        if len(parents) > 2:
            raise ValueError("merge commit has multiple parents; use explicit --base and --head")
        base = parents[1] if len(parents) == 2 else None
        result.update(mode="single-commit", comparison="commit parent", diff_base_sha=base, target_sha=target)
        if base:
            result["paths"] = path_list(run_git(repo, "diff", "--name-only", "-z", base, target, "--"))
        else:
            result["paths"] = path_list(run_git(repo, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "-z", target))
    else:
        requested_base = sha(repo, args.base)
        target = sha(repo, args.head or "HEAD")
        base = requested_base
        if args.merge_base:
            bases = decoded(run_git(repo, "merge-base", "--all", requested_base, target)).splitlines()
            if len(bases) != 1:
                raise ValueError("merge-base is absent or ambiguous; specify an exact comparison base")
            base = bases[0]
        result.update(mode="range", comparison="merge-base" if args.merge_base else "direct",
                      requested_base_sha=requested_base, diff_base_sha=base, target_sha=target)
        result["paths"] = path_list(run_git(repo, "diff", "--name-only", "-z", base, target, "--"))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only local Git scope manifest")
    parser.add_argument("--repo", required=True, type=Path, help="path inside the exact repository to review")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--base", help="explicit comparison base ref/SHA")
    mode.add_argument("--commit", help="single commit to review")
    mode.add_argument("--worktree", action="store_true", help="HEAD plus working tree changes")
    parser.add_argument("--head", help="target ref/SHA; defaults to HEAD with --base")
    parser.add_argument("--merge-base", action="store_true", help="compare target to unique merge-base with --base")
    parser.add_argument("--json", action="store_true", help="print JSON instead of Markdown")
    args = parser.parse_args()
    if (args.head or args.merge_base) and args.base is None:
        parser.error("--head and --merge-base require --base")
    try:
        data = scope(args)
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        parser.exit(2, f"scope unresolved: {exc}\n")
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    print("# 本地代码审查范围（私有）\n")
    for key in ("repository", "branch", "mode", "comparison", "requested_base_sha", "diff_base_sha", "target_sha"):
        print(f"- {key}: {data[key] or '—'}")
    for key in ("paths", "staged", "unstaged", "untracked"):
        print(f"\n## {key} ({len(data[key])})\n")
        for path in data[key]:
            print(f"- {json.dumps(path, ensure_ascii=False)}")
    print("\n仅固定范围；尚未审查 diff 内容、调用链或测试结果。")


if __name__ == "__main__":
    main()
