#!/usr/bin/env python3
"""
PostToolUse hook: keeps docs in step with code.

After Claude edits a file, this hook checks whether the file is one that the
documentation describes. If so, it sends Claude a short note (via
additionalContext) listing the doc pages to update in the same turn.

Exit code 0 always. The hook never blocks an edit; it only adds context.
"""
import json
import sys
from pathlib import PurePosixPath

# Edited path (repo-relative, POSIX style, matched with fnmatch-like rules
# via PurePosixPath.match) -> docs that describe it.
DOC_MAP = [
    ("plants_reminder.py", [
        "docs/how-it-works.md (scheduling logic, seasons)",
        "docs/configuration.md (if PLANTS_CONFIG or settings changed)",
        "docs/troubleshooting.md (if error handling changed)",
    ]),
    ("main.py", [
        "docs/setup.md (if the run/entry-point steps changed)",
        "docs/configuration.md (if configuration changed)",
    ]),
    ("requirements.txt", [
        "docs/setup.md (install steps)",
    ]),
    (".github/workflows/*.yml", [
        "docs/deployment.md (schedule, secrets, workflow steps)",
    ]),
    ("CLAUDE.md", [
        "readme.md (only if project structure or commands changed)",
    ]),
]


def repo_relative(path_str, project_dir):
    """Return a POSIX path relative to the project, or None if outside it."""
    p = path_str.replace("\\", "/")
    if project_dir:
        root = project_dir.replace("\\", "/").rstrip("/") + "/"
        if p.startswith(root):
            p = p[len(root):]
    if p.startswith("/") or p.startswith("../"):
        return None
    return p


def docs_for(rel_path):
    for pattern, docs in DOC_MAP:
        if PurePosixPath(rel_path).match(pattern):
            return docs
    return []


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_input = event.get("tool_input") or {}
    file_path = tool_input.get("file_path")
    if not isinstance(file_path, str) or not file_path:
        return 0

    import os
    rel = repo_relative(file_path, os.environ.get("CLAUDE_PROJECT_DIR", ""))
    if not rel:
        return 0

    docs = docs_for(rel)
    if not docs:
        return 0

    bullets = "\n".join(f"- {d}" for d in docs)
    message = (
        f"You just edited `{rel}`, which the documentation describes. "
        f"Update these docs in this same turn so they match the code:\n"
        f"{bullets}\n"
        f"If the change does not alter any documented behaviour, say so and skip the docs."
    )
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message,
        }
    }
    json.dump(output, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
