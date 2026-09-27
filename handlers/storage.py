"""
Временное хранилище данных пользователей.

ВАЖНО: это просто словари в памяти программы. Как только бот перезапустится
(например, при обновлении на Render) — все данные обнулятся.
Это нормально для начала, но в будущем стоит подключить настоящую базу
данных (например, SQLite), чтобы данные сохранялись всегда.
"""

from datetime import date

# Дата родов (ПДР) каждого пользователя: {user_id: date}
due_dates: dict[int, date] = {}

# Счётчик шевелений сегодня: {user_id: {"date": date, "count": int}}
kicks_data: dict[int, dict] = {}

# История шевелений по прошлым дням: {user_id: [{"date": date, "count": int}, ...]}
kicks_history: dict[int, list] = {}

# Дневник настроения: {user_id: [{"date": date, "mood": str, "note": str|None}, ...]}
mood_entries: dict[int, list] = {}

# Чек-лист в роддом: {user_id: set(индексов отмеченных вещей)}
packed_items: dict[int, set] = {}

# Счётчик схваток: {user_id: [{"start": datetime, "end": datetime|None}, ...]}
contractions_data: dict[int, list] = {}

# Письма малышу: {user_id: [{"date": date, "text": str}, ...]}
letters: dict[int, list] = {}

# Имя пользователя: {user_id: str}
user_names: dict[int, str] = {}

# Вопросы для врача: {user_id: [{"text": str, "asked": bool}, ...]}
doctor_questions: dict[int, list] = {}

# Чек-лист дел до родов: {user_id: set(индексов отмеченных дел)}
prep_items: dict[int, set] = {}

# Напоминания: {user_id: {"water": {...}, "vitamins": {...}, "custom": [...]}}
reminders_data: dict[int, dict] = {}

# Симптомы сегодня: {user_id: {"date": date, "symptoms": set(ключей)}}
symptoms_today: dict[int, dict] = {}

# История симптомов по дням: {user_id: [{"date": date, "symptoms": set(ключей)}, ...]}
symptoms_history: dict[int, list] = {}
# === Сохранение и загрузка всех данных (для настоящей базы данных) ===
import json
from datetime import date, datetime


def _default(obj):
    if isinstance(obj, datetime):
        return {"__type__": "datetime", "value": obj.isoformat()}
    if isinstance(obj, date):
        return {"__type__": "date", "value": obj.isoformat()}
    if isinstance(obj, set):
        return {"__type__": "set", "value": list(obj)}
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _object_hook(d):
    obj_type = d.get("__type__")
    if obj_type == "date":
        return date.fromisoformat(d["value"])
    if obj_type == "datetime":
        return datetime.fromisoformat(d["value"])
    if obj_type == "set":
        return set(d["value"])
    return d


def export_state() -> str:
    """Собирает все данные бота в одну строку для сохранения в базу."""
    state = {
        "due_dates": due_dates,
        "kicks_data": kicks_data,
        "kicks_history": kicks_history,
        "mood_entries": mood_entries,
        "packed_items": packed_items,
        "contractions_data": contractions_data,
        "letters": letters,
        "user_names": user_names,
        "doctor_questions": doctor_questions,
        "prep_items": prep_items,
        "symptoms_today": symptoms_today,
        "symptoms_history": symptoms_history,
        "reminders_data": reminders_data,
    }
    return json.dumps(state, default=_default)


def import_state(raw: str):
    """Загружает ранее сохранённые данные обратно в память бота."""
    if not raw:
        return

    state = json.loads(raw, object_hook=_object_hook)

    def _int_keys(d):
        return {int(k): v for k, v in d.items()}

    due_dates.clear()
    due_dates.update(_int_keys(state.get("due_dates", {})))

    kicks_data.clear()
    kicks_data.update(_int_keys(state.get("kicks_data", {})))

    kicks_history.clear()
    kicks_history.update(_int_keys(state.get("kicks_history", {})))

    mood_entries.clear()
    mood_entries.update(_int_keys(state.get("mood_entries", {})))

    packed_items.clear()
    packed_items.update(_int_keys(state.get("packed_items", {})))

    contractions_data.clear()
    contractions_data.update(_int_keys(state.get("contractions_data", {})))

    letters.clear()
    letters.update(_int_keys(state.get("letters", {})))

    user_names.clear()
    user_names.update(_int_keys(state.get("user_names", {})))

    doctor_questions.clear()
    doctor_questions.update(_int_keys(state.get("doctor_questions", {})))

    prep_items.clear()
    prep_items.update(_int_keys(state.get("prep_items", {})))

    symptoms_today.clear()
    symptoms_today.update(_int_keys(state.get("symptoms_today", {})))

    symptoms_history.clear()
    symptoms_history.update(_int_keys(state.get("symptoms_history", {})))

    reminders_data.clear()
    reminders_data.update(_int_keys(state.get("reminders_data", {})))