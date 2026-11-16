# Configuration

All settings live at the top of `plants_reminder.py`.

## Plants

Plants are defined in `PLANTS_CONFIG`:

```python
"פוטוס זהוב": {
    "summer_days": 7,
    "winter_days": 14,
    "note": 'להשקות כשהחלק העליון (2-3 ס"מ) יבש. לגזום עלים צהובים',
},
```

| Plant | Summer interval | Winter interval | Care focus |
| :--- | :---: | :---: | :--- |
| Golden Pothos (פוטוס זהוב) | 7 days | 14 days | Water when top 2–3 cm is dry |
| Croton (קרוטון) | 5 days | 9 days | Keep substrate lightly moist, avoid AC drafts |
| Snake Plant (סנסוויריה) | 18 days | 35 days | Let the mix dry completely to the bottom |
| Mammillaria Cactus (קקטוס ממילריה) | 18 days | 35 days | Dry out fully, empty drainage water |

> **Keep plant name keys stable.** Watering history is matched by the task title (`🪴 השקיה: <name>`). Renaming a key resets that plant's schedule to today, because its past completions are no longer found.

## Other settings

| Setting | Default | Meaning |
| :--- | :--- | :--- |
| `TASK_HOUR` | `9` | Hour (Israel time) the reminder is due |
| `TIMEZONE` | `Asia/Jerusalem` | Timezone for dates and seasons |
| `TASKLIST_ID` | `@default` | Google Tasks list to use (the primary list) |
