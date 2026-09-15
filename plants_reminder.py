import os
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ============================================================
# הגדרות
# ============================================================
SCOPES = [
    "https://www.googleapis.com/auth/tasks",
]
TIMEZONE = ZoneInfo("Asia/Jerusalem")
UTC_TZ = ZoneInfo("UTC")
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
# פונקציות עזר - תאריכים ועונות
# ============================================================
def now_local():
    """מחזירה את התאריך והשעה הנוכחיים בישראל"""
    return datetime.now(TIMEZONE)

def is_summer(date_obj):
    """
    עונת קיץ: מאי עד אוקטובר
    עונת חורף: נובמבר עד אפריל
    """
    return 5 <= date_obj.month <= 10

def get_interval_days(plant_config, date_obj):
    """בוחרת את מרווח ההשקיה לפי עונת השנה"""
    if is_summer(date_obj):
        return plant_config["summer_days"]
    return plant_config["winter_days"]

def adjust_for_saturday(target_date):
    """אם תאריך היעד נופל על יום שבת, דוחה ליום ראשון"""
    if target_date.weekday() == 5:
        return target_date + timedelta(days=1)
    return target_date

def create_due_datetime(target_date):
    """מייצרת תאריך עם השעה שהוגדרה ומווסתת לזמן אוניברסלי (UTC)"""
    local_datetime = datetime.combine(
        target_date, time(hour=TASK_HOUR), tzinfo=TIMEZONE
    )
    return local_datetime.astimezone(UTC_TZ)

def parse_google_datetime(dt_str):
    """קוראת תאריכים שחוזרים מגוגל בצורה בטוחה (מונע קריסות)"""
    if not dt_str:
        return None
    try:
        clean_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(clean_str)
    except Exception as e:
        print(f"⚠️ שגיאה בפירסור תאריך ({dt_str}): {e}")
        return None

# ============================================================
# תקשורת עם Google Tasks API
# ============================================================
def get_tasks_service():
    """מתחברת לשירות גוגל עם פרטי הגישה"""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("tasks", "v1", credentials=creds)

def get_all_tasks(service, show_completed=False):
    """שולפת משימות. אם show_completed מופעל - שולפת גם משימות מוסתרות שבוצעו"""
    all_tasks = []
    page_token = None

    while True:
        request_args = {
            "tasklist": TASKLIST_ID,
            "showCompleted": show_completed,
            "showHidden": show_completed,  # <--- לוודא שהשורה הזו קיימת
            "pageToken": page_token,
        }

        response = service.tasks().list(**request_args).execute()
        all_tasks.extend(response.get("items", []))
        page_token = response.get("nextPageToken")

        if not page_token:
            break

    return all_tasks

# ============================================================
# ניהול משימות והשקיות
# ============================================================
def get_last_completed_dates(service):
    """מוצאת את התאריך האחרון בו הושלמה השקיה, עבור כל צמח"""
    completed_dates = {}
    try:
        tasks = get_all_tasks(service, show_completed=True)
        for task in tasks:
            title = task.get("title", "")
            status = task.get("status")
            completed_time = task.get("completed")

            if not title.startswith("🪴 השקיה:") or status != "completed":
                continue

            plant_name = title.replace("🪴 השקיה:", "", 1).strip()
            completed_datetime = parse_google_datetime(completed_time)

            if not completed_datetime:
                continue

            completed_date = completed_datetime.astimezone(TIMEZONE).date()
            previous_date = completed_dates.get(plant_name)
            if previous_date is None or completed_date > previous_date:
                completed_dates[plant_name] = completed_date

    except Exception as error:
        print(f"❌ שגיאה בקריאת משימות שהושלמו: {error}")

    return completed_dates

def get_open_watering_tasks(service):
    """מחזירה רשימה של צמחים שכבר קיימת להם משימה פתוחה"""
    watering_tasks = set()
    try:
        tasks = get_all_tasks(service, show_completed=False)
        for task in tasks:
            title = task.get("title", "")
            status = task.get("status")

            if title.startswith("🪴 השקיה:") and status != "completed":
                plant_name = title.replace("🪴 השקיה:", "", 1).strip()
                if plant_name:
                    watering_tasks.add(plant_name)

    except Exception as error:
        print(f"❌ שגיאה בבדיקת משימות קיימות: {error}")

    return watering_tasks

def calculate_next_watering_date(plant_config, last_completed_date, today):
    """מחשבת את תאריך ההשקיה הבא החל מתאריך ההשקיה בפועל"""
    if last_completed_date is None:
        base_date = today
    else:
        # בסיס החישוב הוא המאוחר מבין התאריכים: תאריך הביצוע בפועל או היום
        base_date = max(last_completed_date, today)

    interval_days = get_interval_days(plant_config, base_date)
    next_watering = base_date + timedelta(days=interval_days)

    return adjust_for_saturday(next_watering)

def create_watering_task(service, plant_name, plant_config, watering_date):
    """מייצרת משימה חדשה ביומן גוגל"""
    due_datetime_utc = create_due_datetime(watering_date)
    task_body = {
        "title": f"🪴 השקיה: {plant_name}",
        "notes": f"דגשי טיפול: {plant_config['note']}",
        "due": due_datetime_utc.isoformat().replace("+00:00", "Z"),
    }
    service.tasks().insert(tasklist=TASKLIST_ID, body=task_body).execute()

# ============================================================
# פונקציה ראשית
# ============================================================
def sync_plants_to_tasks():
    service = get_tasks_service()
    today = now_local().date()

    print(f"📅 תאריך בדיקה: {today.strftime('%d/%m/%Y')}")

    last_completed_dates = get_last_completed_dates(service)
    open_watering_tasks = get_open_watering_tasks(service)

    print(f"🔍 משימות פתוחות כרגע: {list(open_watering_tasks)}")
    print(f"📜 היסטוריית השקיות שהושלמו: {last_completed_dates}")

    for plant_name, plant_config in PLANTS_CONFIG.items():
        if plant_name in open_watering_tasks:
            print(f"⏭️ {plant_name}: קיימת כבר תזכורת פתוחה")
            continue

        last_completed_date = last_completed_dates.get(plant_name)

        if last_completed_date:
            print(f"💧 {plant_name}: השקיה אחרונה בוצעה ב-{last_completed_date.strftime('%d/%m/%Y')}")
        else:
            print(f"💧 {plant_name}: לא נמצאה היסטוריית השקיה ב-Google Tasks")

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
            print(f"✅ נוצרה תזכורת חדשה ל-{plant_name} לתאריך {next_watering.strftime('%d/%m/%Y')} בשעה {TASK_HOUR:02d}:00")
        except Exception as error:
            print(f"❌ שגיאה ביצירת תזכורת ל-{plant_name}: {error}")

if __name__ == "__main__":
    sync_plants_to_tasks()