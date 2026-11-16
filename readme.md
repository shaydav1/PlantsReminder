# 🪴 Smart Plant Watering Reminder

A small Python script that works out when each houseplant needs watering, based on its care profile and the current season, and creates a Google Tasks reminder for it. Tasks sync to Google Calendar and the Google Tasks mobile apps. A GitHub Actions workflow runs it every morning.

## How it works

1. Connects to the Google Tasks API using OAuth.
2. For each plant in `PLANTS_CONFIG`:
   - If an **open** reminder already exists for it, it is skipped.
   - Otherwise, the next watering date is calculated:
     - Find the most recent **completed** reminder for that plant (its watering history).
     - Base date = that completion date, or today if there is none or it is in the past.
     - Add the season's interval (summer or winter) to the base date.
     - If the result falls on Saturday, move it to Sunday.
   - Create a task titled `🪴 השקיה: <plant name>` due at 09:00 Israel time, with the plant's care note in the description.

So completing a reminder in Google Tasks is what drives the next one: the next reminder is created on the next run, counted from the day you actually watered.

### Seasons

| Season | Months (Israel) | Used for |
| :--- | :--- | :--- |
| Summer | May – October | `summer_days` |
| Winter | November – April | `winter_days` |

The season is taken from the base date, not the run date.

## Managed plants

| Plant | Summer interval | Winter interval | Care focus |
| :--- | :---: | :---: | :--- |
| Golden Pothos (פוטוס זהוב) | 7 days | 14 days | Water when top 2–3 cm is dry |
| Croton (קרוטון) | 5 days | 9 days | Keep substrate lightly moist, avoid AC drafts |
| Snake Plant (סנסוויריה) | 18 days | 35 days | Let the mix dry completely to the bottom |
| Mammillaria Cactus (קקטוס ממילריה) | 18 days | 35 days | Dry out fully, empty drainage water |

## Setup

### 1. Requirements

- Python 3.9+ (3.10 is used in CI)
- Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Google Cloud OAuth credentials

1. In the [Google Cloud Console](https://console.cloud.google.com/), create or select a project.
2. Enable the **Google Tasks API**.
3. Configure the **OAuth consent screen**. If the app stays in *Testing* status, add your Google account as a test user (see the note on token expiry below).
4. Create an **OAuth client ID** with application type **Desktop app**.
5. Download the JSON file, rename it to `credentials.json`, and place it in the project root.

### 3. First run (generates `token.json`)

```bash
python main.py
```

A browser window opens asking you to grant access to Google Tasks. After you approve, `token.json` is written to the project root and later runs reuse it (refreshing it automatically when it expires).

## Running daily in GitHub Actions

`.github/workflows/daily_reminder.yml` runs `main.py` every day at 05:00 UTC (08:00 Israel time). It can also be started manually from the **Actions** tab (`workflow_dispatch`).

The workflow needs two repository secrets, containing the full contents of the files:

| Secret | Contents |
| :--- | :--- |
| `GCP_CREDENTIALS` | The contents of `credentials.json` |
| `GCP_TOKEN` | The contents of `token.json` (created by the first local run) |

The workflow writes both files at the start of the job and deletes them at the end, even if the run fails.

> **Token expiry:** Apps still in OAuth *Testing* status can have refresh tokens expire after about 7 days. If the workflow starts failing with auth errors, regenerate `token.json` locally and update the `GCP_TOKEN` secret. Publishing the consent screen avoids this.

## Adding or changing plants

Edit `PLANTS_CONFIG` in `plants_reminder.py`:

```python
"פוטוס זהוב": {
    "summer_days": 7,
    "winter_days": 14,
    "note": 'להשקות כשהחלק העליון (2-3 ס"מ) יבש. לגזום עלים צהובים',
},
```

**Keep the plant name key stable.** Watering history is matched by the task title (`🪴 השקיה: <name>`). If you rename a plant in the config, its past completions are no longer found and scheduling restarts from today.

Other settings at the top of `plants_reminder.py`:

- `TASK_HOUR` – hour (Israel time) the reminder is due. Default `9`.
- `TIMEZONE` – default `Asia/Jerusalem`.
- `TASKLIST_ID` – default `@default`, the primary task list.

## Project structure

```text
PlantsReminder/
├── main.py                     # Entry point; calls sync_plants_to_tasks()
├── plants_reminder.py          # Plant config, scheduling logic, Google Tasks API calls
├── requirements.txt            # Python dependencies
├── .github/workflows/
│   └── daily_reminder.yml      # Daily GitHub Actions run
├── .gitignore                  # Excludes credentials, tokens, caches
├── credentials.json            # OAuth client secret (local only, never commit)
├── token.json                  # OAuth user token (local only, never commit)
├── LICENSE
└── readme.md
```

## Security

`credentials.json` and `token.json` grant access to your Google Tasks. They are listed in `.gitignore`; never commit them or paste their contents anywhere public. If they leak, revoke the OAuth client or the token in your Google account and create new ones.

## Troubleshooting

| Symptom | Likely cause |
| :--- | :--- |
| Browser opens on every run | `token.json` missing or not writable; check the working directory. |
| `invalid_grant` / refresh errors | Token revoked or expired (see Testing-status note). Regenerate `token.json`. |
| No reminder created for a plant | An open reminder for it already exists. Complete or delete it, then rerun. |
| Next date ignores your last watering | The completed task's title doesn't match the config key (renamed plant), or the task was deleted rather than completed. |

Each run prints its decisions (open tasks, completion history, and the date chosen for each plant), which is the quickest way to debug a schedule.

## License

See [LICENSE](LICENSE).
