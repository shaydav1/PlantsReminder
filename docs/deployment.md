# Deployment (GitHub Actions)

`.github/workflows/daily_reminder.yml` runs `main.py` every day at 05:00 UTC (08:00 Israel time). It can also be started manually from the **Actions** tab (`workflow_dispatch`).

## Repository secrets

Add these under **Settings → Secrets and variables → Actions**. Each one holds the full contents of the file:

| Secret | Contents |
| :--- | :--- |
| `GCP_CREDENTIALS` | `credentials.json` |
| `GCP_TOKEN` | `token.json` (created by the first local run, see [Setup](setup.md)) |

The job writes both files at the start and deletes them at the end, even if the run fails.

## Token expiry

Apps still in OAuth *Testing* status can have refresh tokens expire after about 7 days. If the workflow starts failing with auth errors such as `invalid_grant`:

1. Run `python main.py` locally to regenerate `token.json`.
2. Update the `GCP_TOKEN` secret with the new contents.

Publishing the OAuth consent screen avoids this.
