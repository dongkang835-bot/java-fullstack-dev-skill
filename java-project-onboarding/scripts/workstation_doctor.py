#!/usr/bin/env python3
"""Read-only workstation and repository requirements snapshot.

No network requests, installs, project commands, env values, credential files,
remote URLs or application configuration values are read or printed.
Keep the generated report private because directory names may be internal.
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path


TOOLS = {
    "git": ["--version"],
    "java": ["-version"],
    "javac": ["-version"],
    "mvn": ["-version"],
    "gradle": ["--version"],
    "node": ["--version"],
    "npm": ["--version"],
    "pnpm": ["--version"],
    "yarn": ["--version"],
    "docker": ["--version"],
    "python3": ["--version"],
}
MARKERS = {
    "pom.xml", "mvnw", "build.gradle", "build.gradle.kts", "gradlew",
    "settings.gradle", "settings.gradle.kts", "gradle-wrapper.properties",
    "package.json", "package-lock.json",
    "pnpm-lock.yaml", "yarn.lock", ".nvmrc", ".node-version", ".java-version",
    ".tool-versions", ".gitmodules", ".gitattributes", "compose.yaml",
    "compose.yml", "docker-compose.yml", "Dockerfile",
}
SKIP = {".git", "node_modules", "target", "build", "dist", "out", ".venv", "venv", "__pycache__"}


def version(tool: str, args: list[str]) -> str:
    executable = shutil.which(tool)
    if not executable:
        return "未找到"
    try:
        result = subprocess.run([executable, *args], capture_output=True, text=True,
                                timeout=5, check=False)
        lines = (result.stdout + "\n" + result.stderr).splitlines()
        first = next((line.strip() for line in lines if line.strip()), "无版本输出")
        return first[:120] if result.returncode == 0 else f"版本命令失败（退出码 {result.returncode}）"
    except (OSError, subprocess.TimeoutExpired):
        return "版本命令不可用或超时"


def markers(root: Path) -> list[Path]:
    found = []
    for base, dirs, files in os.walk(root, followlinks=False):
        path = Path(base)
        depth = len(path.relative_to(root).parts)
        dirs[:] = [d for d in dirs if d not in SKIP and not (path / d).is_symlink()]
        if depth >= 4:
            dirs[:] = []
        for name in files:
            p = path / name
            if name in MARKERS and not p.is_symlink():
                found.append(p)
    return sorted(found)


def hints(path: Path) -> list[str]:
    try:
        if path.name == "package.json":
            data = json.loads(path.read_text(encoding="utf-8"))
            out = []
            engines = data.get("engines") or {}
            for key in ("node", "npm", "pnpm", "yarn"):
                value = engines.get(key) if isinstance(engines, dict) else None
                if isinstance(value, str) and len(value) <= 40:
                    out.append(f"{key}={value}")
            manager = data.get("packageManager")
            if isinstance(manager, str) and re.fullmatch(r"(?:npm|pnpm|yarn)@[\w.+-]+", manager):
                out.append(f"packageManager={manager}")
            return out
        if path.name == "pom.xml":
            content = path.read_text(encoding="utf-8", errors="ignore")[:250000]
            out = []
            for key in ("maven.compiler.release", "maven.compiler.source", "java.version"):
                match = re.search(r"<" + re.escape(key) + r">\s*([^<\s]+)\s*</" + re.escape(key) + r">", content)
                if match and re.fullmatch(r"[\w.$-]{1,40}", match.group(1)):
                    out.append(f"{key}={match.group(1)}")
            return out
        if path.name in {".nvmrc", ".node-version", ".java-version"}:
            value = path.read_text(encoding="utf-8").strip()
            return [f"version={value}"] if re.fullmatch(r"[\w.+-]{1,40}", value) else []
        if path.name == ".tool-versions":
            result = []
            for line in path.read_text(encoding="utf-8").splitlines():
                m = re.fullmatch(r"(java|nodejs)\s+([\w.+-]{1,40})", line.strip())
                if m:
                    result.append(f"{m.group(1)}={m.group(2)}")
            return result
        if path.name == "gradle-wrapper.properties":
            content = path.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"gradle-([\w.+-]+)-(?:bin|all)\.zip", content)
            return [f"Gradle={m.group(1)}"] if m else []
    except (OSError, ValueError, UnicodeError):
        pass
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only Java/full-stack workstation inventory")
    parser.add_argument("--project", type=Path, help="optional cloned project/workspace directory")
    args = parser.parse_args()
    root = args.project.expanduser().resolve() if args.project else None
    if root and not root.is_dir():
        parser.error("--project must be an existing directory")

    print("# 工作站与项目环境盘点（私有）\n")
    print("本脚本不联网、不安装软件、不运行项目命令；候选版本需与 CI 和团队文档核对。\n")
    print(f"- 系统：{platform.system()} {platform.release()}")
    print(f"- 架构：{platform.machine()}")
    print("\n## 已发现的工具\n")
    for name, args in TOOLS.items():
        print(f"- {name}: {version(name, args)}")
    if root:
        files = markers(root)
        names = {p.name for p in files}
        print("\n## 仓库构建线索\n")
        for path in files[:100]:
            relative = path.relative_to(root).as_posix()
            detail = ", ".join(hints(path))
            print(f"- `{relative}`" + (f"：{detail}" if detail else ""))
        if len(files) > 100:
            print(f"- 另有 {len(files) - 100} 个线索文件未列出")
        print("\n## 下一步核对\n")
        if "pom.xml" in names or "build.gradle" in names or "build.gradle.kts" in names:
            print("- 核对 JDK 版本/发行版、IDE SDK 和构建器实际使用的 JDK")
        if "pom.xml" in names:
            print("- Maven：" + ("发现项目 Wrapper，先核对 ./mvnw -v" if "mvnw" in names else "未发现 Wrapper，向团队核对 Maven 安装版本"))
        if "build.gradle" in names or "build.gradle.kts" in names:
            print("- Gradle：" + ("发现项目 Wrapper，先核对 ./gradlew --version" if "gradlew" in names else "未发现 Wrapper，向团队核对 Gradle 安装版本"))
        if "package.json" in names:
            manager = "pnpm" if "pnpm-lock.yaml" in names else "yarn" if "yarn.lock" in names else "npm" if "package-lock.json" in names else "待确认"
            print(f"- 前端：核对 Node 版本与包管理器；锁文件提示 {manager}")
        if ".gitmodules" in names:
            print("- 子模块：核对 git submodule status --recursive，并保持主仓固定的提交")
        if "compose.yaml" in names or "compose.yml" in names or "docker-compose.yml" in names:
            print("- 容器：确认是否需要本地运行及其连接的数据库/消息服务环境")
    else:
        print("\n尚未提供项目目录；拉仓后用 --project 再盘点项目版本和构建线索。")


if __name__ == "__main__":
    main()
