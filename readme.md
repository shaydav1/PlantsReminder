# 🪴 Smart Plant Watering Reminder

A small Python script that works out when each houseplant needs watering, based on its care profile and the season, and creates a Google Tasks reminder for it. Reminders sync to Google Calendar and the Google Tasks apps. A GitHub Actions workflow runs it every morning.

## Quick start

```bash
pip install -r requirements.txt
# place credentials.json in the project root, then:
python main.py
```

The first run opens a browser to authorize Google Tasks and creates `token.json`.

## Documentation

- [How it works](docs/how-it-works.md): scheduling logic and seasons
- [Setup](docs/setup.md): Google Cloud credentials and first run
- [Deployment](docs/deployment.md): daily GitHub Actions run and secrets
- [Configuration](docs/configuration.md): managed plants and settings
- [Troubleshooting](docs/troubleshooting.md): common errors

## Project structure

```text
PlantsReminder/
├── main.py                     # Entry point
├── plants_reminder.py          # Plant config, scheduling, Google Tasks API calls
├── requirements.txt            # Python dependencies
├── .github/workflows/
│   └── daily_reminder.yml      # Daily GitHub Actions run
├── docs/                       # Project documentation
├── .gitignore                  # Excludes credentials, tokens, caches
├── LICENSE
└── readme.md
```

## Security

`credentials.json` and `token.json` grant access to your Google Tasks. They are git-ignored. Never commit them or paste their contents anywhere public. If they leak, revoke the OAuth client or token in your Google account and create new ones.

## License

See [LICENSE](LICENSE).
