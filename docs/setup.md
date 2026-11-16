# Setup

## 1. Requirements

- Python 3.9+ (CI uses 3.10)
- Dependencies:

```bash
pip install -r requirements.txt
```

## 2. Google Cloud OAuth credentials

1. In the [Google Cloud Console](https://console.cloud.google.com/), create or select a project.
2. Enable the **Google Tasks API**.
3. Configure the **OAuth consent screen**. If the app stays in *Testing* status, add your Google account as a test user (see [Deployment](deployment.md#token-expiry)).
4. Create an **OAuth client ID** with application type **Desktop app**.
5. Download the JSON file, rename it to `credentials.json`, and place it in the project root.

## 3. First run (creates `token.json`)

```bash
python main.py
```

A browser window opens asking you to grant access to Google Tasks. After you approve, `token.json` is written to the project root. Later runs reuse it and refresh it automatically when it expires.

Both `credentials.json` and `token.json` are git-ignored. Never commit them.
