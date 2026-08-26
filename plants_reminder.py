import os
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ============================================================
# Configuration
# ============================================================
SCOPES = [
    "https://www.googleapis.com/auth/tasks",
]
TIMEZONE = ZoneInfo("Asia/Jerusalem")
TASKLIST_ID = "@default"
TASK_HOUR = 9

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
        "note": 'להשקות כשהחלק העליון (2-3 ס"מ) יבש. לגזום עלים צהובים',
    },
    "קרוטון": {
        "summer_days": 5,
        "winter_days": 9,
        "note": "לשמור על לחות קלה במצע, להרחיק מזרמי אוויר של מזגן",
    },
}


# ============================================================
# Date / Season helpers
# ============================================================
def now_local():
    """Returns the current date/time in Israel."""
    return datetime.now(TIMEZONE)


def is_summer(date_obj):
    """
    Summer season: May through October.
    Winter season: November through April.
    """
    return 5 <= date_obj.month <= 10


def get_interval_days(plant_config, date_obj):
    """Select watering interval based on the season of the given date."""
    if is_summer(date_obj):
        return plant_config["summer_days"]
    return plant_config["winter_days"]


def adjust_for_saturday(target_date):
    """If the watering date falls on Saturday, move it to Sunday."""
    if target_date.weekday() == 5:  # Saturday
        return target_date + timedelta(days=1)
    return target_date


def create_due_datetime(target_date):
    """Creates a local Israel datetime at 09:00 and converts it to UTC for Google Tasks."""
    local_datetime = datetime.combine(
        target_date, time(hour=TASK_HOUR), tzinfo=TIMEZONE
    )
    return local_datetime.astimezone(ZoneInfo("UTC"))


# ============================================================
# Google Tasks API Setup
# ============================================================
def get_tasks_service():
    """Authenticate and return the Google Tasks service."""
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES,
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build(
        "tasks",
        "v1",
        credentials=creds,
    )


def get_all_tasks(service, show_completed=False):
    """Retrieve all tasks with proper pagination handling."""
    all_tasks = []
    page_token = None

    while True:
        response = (
            service.tasks()
            .list(
                tasklist=TASKLIST_ID,
                showCompleted=show_completed,
                showHidden=show_completed,
                pageToken=page_token,
            )
            .execute()
        )

        all_tasks.extend(response.get("items", []))
        page_token = response.get("nextPageToken")

        if not page_token:
            break

    return all_tasks


# ============================================================
# Task Processing & Scheduling
# ============================================================
def get_last_completed_dates(service):
    """Find the most recent completed watering date for each plant."""
    completed_dates = {}

    try:
        tasks = get_all_tasks(service, show_completed=True)

        for task in tasks:
            title = task.get("title", "")
            status = task.get("status")
            completed_time = task.get("completed")

            if (
                not title.startswith("🪴 השקיה:")
                or status != "completed"
                or not completed_time
            ):
                continue

            plant_name = title.replace("🪴 השקיה:", "", 1).strip()

            try:
                completed_datetime = datetime.fromisoformat(
                    completed_time.replace("Z", "+00:00")
                )
                completed_date = completed_datetime.astimezone(TIMEZONE).date()
            except (ValueError, TypeError):
                print(f"⚠️ לא ניתן לפרש תאריך השלמה עבור: {title}")
                continue

            previous_date = completed_dates.get(plant_name)
            if previous_date is None or completed_date > previous_date:
                completed_dates[plant_name] = completed_date

    except Exception as error:
        print(f"❌ שגיאה בקריאת משימות שהושלמו: {error}")

    return completed_dates


def get_open_watering_tasks(service):
    """Returns a set containing plant names that already have an open watering task."""
    watering_tasks = set()

    try:
        tasks = get_all_tasks(service, show_completed=False)

        for task in tasks:
            title = task.get("title", "")
            if title.startswith("🪴 השקיה:"):
                plant_name = title.replace("🪴 השקיה:", "", 1).strip()
                if plant_name:
                    watering_tasks.add(plant_name)

    except Exception as error:
        print(f"❌ שגיאה בבדיקת משימות קיימות: {error}")

    return watering_tasks


def calculate_next_watering_date(plant_config, last_completed_date, today):
    """Calculate the next valid watering date."""
    if last_completed_date is None:
        next_watering = today
    else:
        interval_days = get_interval_days(plant_config, last_completed_date)
        next_watering = last_completed_date + timedelta(days=interval_days)

        if next_watering < today:
            next_watering = today

    return adjust_for_saturday(next_watering)


def create_watering_task(service, plant_name, plant_config, watering_date):
    """Create a Google Task for the specified plant."""
    due_datetime_utc = create_due_datetime(watering_date)

    task_body = {
        "title": f"🪴 השקיה: {plant_name}",
        "notes": f"דגשי טיפול: {plant_config['note']}",
        "due": due_datetime_utc.isoformat().replace("+00:00", "Z"),
    }

    service.tasks().insert(tasklist=TASKLIST_ID, body=task_body).execute()


# ============================================================
# Main Executor
# ============================================================
def sync_plants_to_tasks():
    service = get_tasks_service()
    today = now_local().date()

    print(f"📅 היום: {today.strftime('%d/%m/%Y')}")

    last_completed_dates = get_last_completed_dates(service)
    open_watering_tasks = get_open_watering_tasks(service)

    for plant_name, plant_config in PLANTS_CONFIG.items():
        if plant_name in open_watering_tasks:
            print(f"⏭️ {plant_name}: קיימת כבר תזכורת פתוחה")
            continue

        last_completed_date = last_completed_dates.get(plant_name)

        if last_completed_date:
            print(
                f"💧 {plant_name}: השקיה אחרונה ב-{last_completed_date.strftime('%d/%m/%Y')}"
            )
        else:
            print(f"💧 {plant_name}: לא נמצאה היסטוריית השקיה")

        next_watering = calculate_next_watering_date(
            plant_config=plant_config,
            last_completed_date=last_completed_date,
            today=today,
        )

        try:
            create_watering_task(
                service=service,
                plant_name=plant_name,
                plant_config=plant_config,
                watering_date=next_watering,
            )
            print(
                f"✅ נוצרה תזכורת ל-{plant_name} לתאריך {next_watering.strftime('%d/%m/%Y')} בשעה {TASK_HOUR:02d}:00"
            )
        except Exception as error:
            print(f"❌ שגיאה ביצירת תזכורת ל-{plant_name}: {error}")


if __name__ == "__main__":
    sync_plants_to_tasks()