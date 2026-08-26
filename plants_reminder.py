def main():
    from datetime import datetime, timedelta, timezone
    import os.path
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    SCOPES = [
        "https://www.googleapis.com/auth/tasks",
        "https://www.googleapis.com/auth/calendar",
    ]

    PLANTS_CONFIG = {
        "קקטוס ממילריה": {
            "summer_days": 18,
            "winter_days": 35,
            "note": "לוודא אדמה יבשה לחלוטין ולרוקן עודפים מתחתית העציץ",
        },
        "סנסוויריה (לשון החותנת)": {
            "summer_days": 18,
            "winter_days": 35,
            "note": "לבחון שהמצע יבש לגמרי עד התחתית לפני ההשקיה",
        },
        "פוטוס זהוב": {
            "summer_days": 7,
            "winter_days": 14,
            "note": "להשקות כשהחלק העליון (2-3 ס\"מ) יבש. לגזום עלים צהובים",
        },
        "קרוטון": {
            "summer_days": 5,
            "winter_days": 9,
            "note": "לשמור על לחות קלה במצע, להרחיק מזרמי אוויר של מזגן",
        },
    }

    DEFAULT_FALLBACK_DATE = datetime(2026, 8, 1).date()

    def get_tasks_service():
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return build("tasks", "v1", credentials=creds)

    def is_summer(date_obj=None):
        if date_obj is None:
            date_obj = datetime.now()
        return 5 <= date_obj.month <= 10

    def adjust_for_saturday(target_date):
        """מזיז תזכורת משבת ליום ראשון."""
        if target_date.weekday() == 5:
            target_date += timedelta(days=1)
        return target_date

    def get_last_completed_dates(service):
        """קורא מ-Google Tasks את תאריך ההשקיה האחרון שסומן כהושלם (Completed)."""
        completed_dates = {}
        try:
            tasks_result = service.tasks().list(
                tasklist="@default",
                showCompleted=True,
                showHidden=True
            ).execute()

            items = tasks_result.get("items", [])
            for item in items:
                title = item.get("title", "")
                status = item.get("status")
                completed_time_str = item.get("completed")

                if "השקיה:" in title and status == "completed" and completed_time_str:
                    plant_name = title.replace("🪴 השקיה:", "").strip()
                    completed_dt = datetime.fromisoformat(completed_time_str.replace("Z", "+00:00"))
                    completed_date = completed_dt.date()

                    if plant_name not in completed_dates or completed_date > completed_dates[plant_name]:
                        completed_dates[plant_name] = completed_date
        except Exception as e:
            print(f"שגיאה בקריאת משימות שבוצעו: {e}")

        return completed_dates

    def task_exists_or_future(service, plant_name):
        """בודק אם כבר קיימת תזכורת פתוחה ביומן/משימות כדי למנוע כפילויות."""
        try:
            tasks_result = service.tasks().list(tasklist="@default", showCompleted=False).execute()
            items = tasks_result.get("items", [])
            for item in items:
                if f"השקיה: {plant_name}" in item.get("title", ""):
                    return True
        except Exception as e:
            print(f"שגיאה בבדיקת משימות קיימות: {e}")
        return False

    def sync_plants_to_tasks():
        service = get_tasks_service()
        today = datetime.now().date()
        season = "summer" if is_summer(today) else "winter"

        last_completed = get_last_completed_dates(service)

        for plant_name, config in PLANTS_CONFIG.items():
            if task_exists_or_future(service, plant_name):
                continue

            base_date = last_completed.get(plant_name, DEFAULT_FALLBACK_DATE)
            interval_days = config[f"{season}_days"]

            next_watering = base_date + timedelta(days=interval_days)

            if next_watering < today:
                next_watering = today

            next_watering = adjust_for_saturday(next_watering)

            due_datetime = datetime.combine(next_watering, datetime.min.time()) + timedelta(hours=9)
            due_str = due_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            task_body = {
                "title": f"🪴 השקיה: {plant_name}",
                "notes": f"דגשי טיפול: {config['note']}",
                "due": due_str,
            }

            service.tasks().insert(tasklist="@default", body=task_body).execute()
            print(f"✅ נוצרה תזכורת חדשה ל-{plant_name} לתאריך {next_watering.strftime('%d/%m/%Y')}")

    if __name__ == "__main__":
        sync_plants_to_tasks()

if __name__ == "__main__":
    main()
