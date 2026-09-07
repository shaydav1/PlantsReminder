# 🪴 Smart Plant Watering Reminder

A Python automation script that calculates optimal watering schedules for household plants based on seasonal logic and automatically syncs reminders directly to **Google Tasks** & **Google Calendar**.

---

## ✨ Features

* **Seasonal Watering Logic:** Automatically adjusts watering frequencies based on the current season (Summer vs. Winter).
* **Google Tasks Integration:** Direct integration with Google Tasks API to create task items (with completion checkboxes) that seamlessly sync to Google Calendar on web and iOS/Android devices.
* **Shabbat / Saturday Guard:** Automatically shifts scheduled reminders that fall on Saturday (Shabbat) to Sunday.
* **Plant-Specific Care Notes:** Attaches tailored care guidelines (light requirements, soil moisture, drainage tips) directly to task descriptions.

---

## 🌿 Managed Plants & Care Schedule

| Plant Name | Summer Interval | Winter Interval | Care Focus |
| :--- | :---: | :---: | :--- |
| **Pothos (Golden)** | Every 7 days | Every 14 days | Top 2–3 cm dry before watering |
| **Croton (*Codiaeum variegatum*)** | Every 5 days | Every 9 days | Keep soil lightly moist, avoid cold drafts |
| **Snake Plant (*Sansevieria*)** | Every 18 days | Every 35 days | Allow soil to dry completely to bottom |
| **Mammillaria Cactus** | Every 18 days | Every 35 days | Fully dry soil, clear excess drainage water |

---

## 🛠️ Setup & Installation

### 1. Prerequisites

Ensure Python 3.9+ is installed, then install the Google API client libraries:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 2. Google Cloud Platform Configuration

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the Google Tasks AP.
3. Configure the **OAuth Consent Screen** (set publishing status or test users).
4. Create an **OAuth 2.0 Client ID** with Application Type set to **Desktop App**.
5. Download the JSON credentials file, rename it to `credentials.json`, and place it in the project root directory.

### 3. Running the Script

Execute the script from your terminal or PyCharm: 

```bash
python plants_reminder.py
```

> **Note:** On first run, a browser window will open requesting authorization to manage your Google Tasks and Calendar. Once granted, a `token.json` file will be stored locally for future seamless automated runs.

---

## 📁 Project Structure

```text
PlantsReminder/
├── plants_reminder.py    # Core scheduling logic & Google Tasks API integration
├── credentials.json      # Google Cloud OAuth client secrets (DO NOT COMMIT)
├── token.json            # Generated authorization token (DO NOT COMMIT)
├── .gitignore            # Git ignore configuration
└── README.md             # Project documentation
```

---

## 🛡️ Security Note

Make sure to include `credentials.json` and `token.json` in your `.gitignore` file to avoid exposing private OAuth credentials:

```text
# .gitignore
credentials.json
token.json
__pycache__/
.idea/
.venv/
```
### Smart Task Management
- **Target Task List:** Automatically syncs with your designated Google Tasks list.
- **Duplicate Prevention:** Checks for existing open or recently completed tasks before creating new ones, preventing duplicate reminders on the same day.