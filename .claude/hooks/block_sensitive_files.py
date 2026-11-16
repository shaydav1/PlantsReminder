#!/usr/bin/env python3
"""
PreToolUse hook: blocks Claude Code from reading sensitive files.

Claude Code sends the tool call as JSON on stdin. Exit code 2 blocks the
call and sends the stderr message back to Claude. Exit code 0 allows it.
"""
import fnmatch
import json
import re
import sys
from pathlib import PurePosixPath

# File name patterns (matched against the file name only, case-insensitive).
SENSITIVE_NAME_PATTERNS = [
    ".env", ".env.*",
    "*.pem", "*.key", "*.p12", "*.pfx", "*.kdbx",
    "id_rsa", "id_rsa.*", "id_dsa", "id_ecdsa", "id_ed25519", "id_ed25519.*",
    "credentials", "credentials.json",
    "secrets.json", "secrets.yml", "secrets.yaml", "secrets.toml",
    ".netrc", ".npmrc", ".pypirc", ".git-credentials",
]

# Directories whose contents are always sensitive.
SENSITIVE_DIRS = {".ssh", ".aws", ".gnupg", ".azure", ".kube"}

# Templates that contain no real secrets and may be read.
ALLOWED_NAMES = {".env.example", ".env.sample", ".env.template"}


def is_sensitive(path_str):
    if not path_str or not isinstance(path_str, str):
        return False

    posix = PurePosixPath(path_str.replace("\\", "/"))
    name = posix.name.lower()

    if name in ALLOWED_NAMES:
        return False

    if any(part.lower() in SENSITIVE_DIRS for part in posix.parts):
        return True

    return any(fnmatch.fnmatch(name, pat) for pat in SENSITIVE_NAME_PATTERNS)


def find_sensitive_reference(tool_name, tool_input):
    """Return the offending path/token, or None if the call is allowed."""
    if tool_name == "Read":
        path = tool_input.get("file_path", "")
        return path if is_sensitive(path) else None

    if tool_name == "Grep":
        for key in ("path", "glob"):
            value = tool_input.get(key, "")
            if is_sensitive(value):
                return value
        return None

    if tool_name == "Glob":
        for key in ("path", "pattern"):
            value = tool_input.get(key, "")
            if is_sensitive(value):
                return value
        return None

    if tool_name == "Bash":
        # Split the command into rough tokens and check each one,
        # so commands like "cat .env" or "type C:\\x\\id_rsa" are caught.
        command = tool_input.get("command", "") or ""
        for token in re.split(r"[\s;&|<>()`\"']+", command):
            if is_sensitive(token):
                return token
        return None

    return None


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        # Not a hook payload we understand: do not block.
        return 0

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}

    offending = find_sensitive_reference(tool_name, tool_input)
    if offending is None:
        return 0

    print(
        f"BLOCKED by block_sensitive_files hook: '{offending}' looks like a "
        "sensitive file (secrets, keys or credentials). Do not read it. "
        "Ask the user to provide the values they need, or use a template "
        "such as .env.example instead.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
