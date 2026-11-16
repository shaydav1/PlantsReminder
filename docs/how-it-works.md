# How It Works

Each run of `sync_plants_to_tasks()` checks Google Tasks and creates at most one watering reminder per plant.

1. **Authenticate.** The script connects to the Google Tasks API using OAuth (`get_tasks_service`).
2. **Read history.** It reads completed tasks titled `🪴 השקיה: <plant>` and records the latest completion date per plant.
3. **Skip open reminders.** If a plant already has an open (not completed) reminder, it is skipped.
4. **Calculate the next date.**
   - Base date = last completion date, or today if there is no history or the last completion is in the past.
   - Interval = `summer_days` or `winter_days`, chosen by the season of the base date.
   - Next date = base date + interval. If it falls on Saturday, it moves to Sunday.
5. **Create the task.** The task is due at 09:00 Israel time (`TASK_HOUR`) and its description contains the plant's care note.

Completing a reminder in Google Tasks is what drives the next one. The next reminder is created on the first run after the previous one is completed, counted from the day you actually watered.

## Seasons

| Season | Months (Israel) | Interval used |
| :--- | :--- | :--- |
| Summer | May – October | `summer_days` |
| Winter | November – April | `winter_days` |

The season is taken from the base date, not the run date.
