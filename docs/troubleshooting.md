# Troubleshooting

| Symptom | Likely cause and fix |
| :--- | :--- |
| Browser opens on every run | `token.json` is missing or not writable. Check that you run from the project root. |
| `invalid_grant` or refresh errors | Token revoked or expired, often because of the Testing-status expiry. Regenerate `token.json` (see [Deployment](deployment.md#token-expiry)). |
| No reminder created for a plant | An open reminder for it already exists. Complete or delete it, then rerun. |
| Next date ignores your last watering | The completed task's title doesn't match the config key (renamed plant), or the reminder was deleted instead of completed. |

Each run prints what it decided: open reminders, completion history, and the date chosen for each plant. This is the quickest way to debug a schedule.
