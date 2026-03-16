from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TASK_ID_RE = re.compile(r"^task_id:\s*(?P<task_id>.+?)\s*$")
CHECK_CMD_RE = re.compile(r"^-\s*\[.\]\s*`(?P<command>.+?)`\s*$")


def _iter_markdown_files(repo_root: Path) -> list[Path]:
    return sorted(path for path in repo_root.rglob("*.md") if path.is_file())


def _extract_task_id(text: str) -> str | None:
    for line in text.splitlines():
        match = TASK_ID_RE.match(line.strip())
        if match:
            return match.group("task_id")
    return None


def _extract_acceptance_commands(text: str) -> list[str]:
    commands: list[str] = []
    for line in text.splitlines():
        match = CHECK_CMD_RE.match(line.strip())
        if match:
            commands.append(match.group("command"))
    return commands


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _cmd_scan(repo_root: Path) -> int:
    markdown_files = _iter_markdown_files(repo_root)
    tasks: list[dict[str, str]] = []

    for file_path in markdown_files:
        text = _read_text(file_path)
        if text is None:
            continue
        task_id = _extract_task_id(text)
        if task_id is None:
            continue
        tasks.append(
            {
                "task_id": task_id,
                "file": str(file_path.relative_to(repo_root)).replace("\\", "/"),
            }
        )

    result = {
        "ok": True,
        "repo_root": str(repo_root.resolve()),
        "task_count": len(tasks),
        "tasks": tasks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _cmd_verify_task(repo_root: Path, task_id: str) -> int:
    markdown_files = _iter_markdown_files(repo_root)

    for file_path in markdown_files:
        text = _read_text(file_path)
        if text is None:
            continue

        discovered_task_id = _extract_task_id(text)
        if discovered_task_id != task_id:
            continue

        acceptance_commands = _extract_acceptance_commands(text)
        checks = [
            {
                "name": command,
                "status": "pending",
            }
            for command in acceptance_commands
        ]
        result = {
            "ok": True,
            "task_id": task_id,
            "task_file": str(file_path.relative_to(repo_root)).replace("\\", "/"),
            "checks": checks,
            "summary": {
                "total": len(checks),
                "passed": 0,
                "pending": len(checks),
                "failed": 0,
            },
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    result = {
        "ok": False,
        "task_id": task_id,
        "error": f"Task '{task_id}' not found",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SmartWorkmate maintenance helpers")
    parser.add_argument("--repo-root", default=".", help="Repository root path")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("scan", help="Scan markdown tasks in repository")

    verify_parser = subparsers.add_parser(
        "verify-task", help="Verify task metadata and acceptance checks"
    )
    verify_parser.add_argument("--task-id", required=True, help="Task identifier")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists() or not repo_root.is_dir():
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": f"Invalid repo root: {repo_root}",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    if args.command == "scan":
        return _cmd_scan(repo_root)
    if args.command == "verify-task":
        return _cmd_verify_task(repo_root, args.task_id)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
