#!/usr/bin/env python3
"""
Notification hook: plays a sound when Claude Code needs the user's attention
(permission prompts, idle prompts, etc.).

The hook runs asynchronously so it never delays Claude. Failures are silent,
so a sound problem can't break the session.
"""
import sys

SOUND_ALIAS = "SystemExclamation"  # other Windows aliases: SystemAsterisk, SystemHand, SystemQuestion


def main():
    try:
        import winsound  # Windows only
    except ImportError:
        return 0

    try:
        winsound.PlaySound(SOUND_ALIAS, winsound.SND_ALIAS | winsound.SND_ASYNC)
    except RuntimeError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
