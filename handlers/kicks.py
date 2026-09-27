from datetime import date
from aiogram import Router, F
from aiogram.types import CallbackQuery

from handlers.storage import kicks_data, kicks_history, due_dates
from handlers.keyboards import kicks_menu_kb

router = Router()

TOTAL_PREGNANCY_DAYS = 280


def _get_current_week(user_id: int):
    due_date = due_dates.get(user_id)
    if not due_date:
        return None
    days_left = (due_date - date.today()).days
    days_pregnant = TOTAL_PREGNANCY_DAYS - days_left
    return max(0, days_pregnant // 7)


def _ensure_today(user_id: int) -> dict:
    today = date.today()
    entry = kicks_data.get(user_id)

    if entry and entry["date"] != today:
        # день сменился — сохраняем вчерашний результат в историю
        history = kicks_history.setdefault(user_id, [])
        history.append({"date": entry["date"], "count": entry["count"]})
        kicks_data[user_id] = {"date": today, "count": 0}
    elif not entry:
        kicks_data[user_id] = {"date": today, "count": 0}

    return kicks_data[user_id]


def get_today_count(user_id: int) -> int:
    return _ensure_today(user_id)["count"]


def get_week_note(user_id: int) -> str:
    week = _get_current_week(user_id)

    if week is None:
        return (
            "Кстати, если укажешь дату родов в «📅 Мой срок» — подскажу, чего "
            "ожидать по шевелениям именно на твоём сроке."
        )

    if week < 16:
        return (
            f"Сейчас у тебя примерно {week}-я неделя — обычно шевеления начинают "
            "чувствоваться где-то между 16 и 25 неделей, так что пока не заметить "
            "их совсем — совершенно нормально. Здорово, что уже заглянула сюда "
            "заранее! Можешь сбросить счётчик и вернуться, когда будет актуальнее 💛"
        )

    if week < 28:
        return (
            f"На {week}-й неделе шевеления обычно уже ощущаются, но могут быть "
            "ещё нерегулярными и мягкими — это нормально, малыш пока небольшой. "
            "Ближе к 28-й неделе движения станут заметнее и чаще."
        )

    return (
        f"На {week}-й неделе многие врачи советуют ориентироваться на простое "
        "правило: около 10 шевелений за 2 часа — обычно неплохой ориентир, но "
        "норма у каждой своя, лучше уточнить у своего врача, что подходит именно "
        "тебе. Если шевелений заметно меньше обычного — не откладывай, скажи врачу."
    )


@router.callback_query(F.data == "kicks:menu")
async def cb_kicks_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    count = get_today_count(user_id)
    note = get_week_note(user_id)

    text = (
        f"🦶 Сегодня отмечено шевелений: {count}\n\n"
        "Нажимай «➕» каждый раз, когда почувствуешь толчок. Счётчик обнуляется "
        f"каждый новый день, а прошлые дни сохраняются в истории.\n\n{note}"
    )

    await callback.message.edit_text(text, reply_markup=kicks_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "kicks:add")
async def cb_kicks_add(callback: CallbackQuery):
    user_id = callback.from_user.id
    entry = _ensure_today(user_id)
    entry["count"] += 1

    note = get_week_note(user_id)
    text = f"🦶 Сегодня отмечено шевелений: {entry['count']}\n\n{note}"

    await callback.message.edit_text(text, reply_markup=kicks_menu_kb())
    await callback.answer("Отмечено!")


@router.callback_query(F.data == "kicks:history")
async def cb_kicks_history(callback: CallbackQuery):
    user_id = callback.from_user.id
    today_entry = _ensure_today(user_id)
    history = kicks_history.get(user_id, [])

    all_entries = history + [today_entry]
    last_entries = all_entries[-7:][::-1]

    lines = ["📜 Шевеления за последние дни:\n"]
    for entry in last_entries:
        date_str = entry["date"].strftime("%d.%m")
        suffix = " (сегодня)" if entry["date"] == date.today() else ""
        lines.append(f"{date_str}{suffix} — {entry['count']}")

    await callback.message.edit_text("\n".join(lines), reply_markup=kicks_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "kicks:reset")
async def cb_kicks_reset(callback: CallbackQuery):
    user_id = callback.from_user.id
    kicks_data.pop(user_id, None)

    await callback.message.edit_text(
        "Счётчик обнулён. Сегодня отмечено шевелений: 0 🦶",
        reply_markup=kicks_menu_kb(),
    )
    await callback.answer()