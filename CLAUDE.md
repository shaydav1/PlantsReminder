# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

Python script that calculates watering schedules for houseplants and creates Google Tasks reminders via the Google Tasks API. Runs locally (`python main.py`) and daily in GitHub Actions (`.github/workflows/daily_reminder.yml`).

Key files:
- `plants_reminder.py`: plant config, scheduling logic, Google Tasks API calls
- `main.py`: entry point
- `docs/`: user documentation (see `readme.md` for the index)

## Rules

- **Plant name keys in `PLANTS_CONFIG` are Hebrew and act as IDs.** Watering history is matched by the task title `🪴 השקיה: <name>`. Do not rename or retranslate a key without also migrating existing tasks, or the schedule resets.
- **Keep Hebrew comments, strings, and task titles as they are.** Do not translate them.
- **Never commit or print `credentials.json` or `token.json`.** Both are git-ignored and grant access to the user's Google Tasks.
- **Put user-facing documentation in `docs/`**, and keep `readme.md` as a short index that links to it.
- **Don't change scheduling rules** (seasons, Saturday shift to Sunday, base date) without asking. They are the core behavior.
- **Don't commit or push unless asked.**

## Commands

```bash
pip install -r requirements.txt   # install dependencies
python main.py                    # run once locally (creates token.json on first run)
```

There is no test suite or linter configured.

## Gotchas

- `requirements.txt` is UTF-16 encoded. pip reads it fine, but edit with care.
- Google OAuth apps in *Testing* status expire refresh tokens after about 7 days. The CI failure mode is `invalid_grant`.
