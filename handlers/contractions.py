from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery

from handlers.storage import contractions_data
from handlers.keyboards import contractions_menu_kb

router = Router()


def format_duration(seconds: int) -> str:
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes} мин {secs} сек"


def get_status_text(user_id: int) -> str:
    entries = contractions_data.get(user_id, [])

    if not entries:
        return (
            "⏱ Отмечай начало и конец каждой схватки — так будет проще увидеть, "
            "как часто они повторяются и сколько длятся.\n\n"
            "Нажми «▶️ Начать схватку», когда почувствуешь, что она началась."
        )

    last = entries[-1]

    if last["end"] is None:
        elapsed = int((datetime.now() - last["start"]).total_seconds())
        return (
            f"⏱ Схватка идёт: {format_duration(elapsed)}\n\n"
            "Нажми «⏹ Закончить схватку», когда она пройдёт."
        )

    lines = ["⏱ Последние схватки:\n"]
    finished = [e for e in entries if e["end"] is not None]

    for entry in finished[-5:]:
        duration = int((entry["end"] - entry["start"]).total_seconds())
        line = f"{entry['start'].strftime('%H:%M')} — длилась {format_duration(duration)}"

        idx_in_all = entries.index(entry)
        if idx_in_all > 0:
            prev = entries[idx_in_all - 1]
            interval_min = int((entry["start"] - prev["start"]).total_seconds() // 60)
            line += f", через {interval_min} мин после предыдущей"

        lines.append(line)

    lines.append(
        "\n💡 Ориентир (но не замена консультации с врачом): если схватки идут "
        "примерно каждые 5 минут, длятся около минуты и это продолжается час — "
        "обычно это сигнал собираться в роддом. Уточни этот момент заранее у своего врача."
    )
    lines.append("\nНажми «▶️ Начать схватку», когда начнётся следующая.")
    return "\n".join(lines)


@router.callback_query(F.data == "contractions:menu")
async def cb_contractions_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    entries = contractions_data.get(user_id, [])
    active = bool(entries) and entries[-1]["end"] is None

    await callback.message.edit_text(
        get_status_text(user_id),
        reply_markup=contractions_menu_kb(active),
    )
    await callback.answer()


@router.callback_query(F.data == "contractions:start")
async def cb_contractions_start(callback: CallbackQuery):
    user_id = callback.from_user.id
    entries = contractions_data.setdefault(user_id, [])
    entries.append({"start": datetime.now(), "end": None})

    await callback.message.edit_text(
        get_status_text(user_id),
        reply_markup=contractions_menu_kb(active=True),
    )
    await callback.answer("Начали отсчёт!")


@router.callback_query(F.data == "contractions:stop")
async def cb_contractions_stop(callback: CallbackQuery):
    user_id = callback.from_user.id
    entries = contractions_data.get(user_id, [])

    if entries and entries[-1]["end"] is None:
        entries[-1]["end"] = datetime.now()

    await callback.message.edit_text(
        get_status_text(user_id),
        reply_markup=contractions_menu_kb(active=False),
    )
    await callback.answer("Записала")


@router.callback_query(F.data == "contractions:reset")
async def cb_contractions_reset(callback: CallbackQuery):
    user_id = callback.from_user.id
    contractions_data[user_id] = []

    await callback.message.edit_text(
        get_status_text(user_id),
        reply_markup=contractions_menu_kb(active=False),
    )
    await callback.answer("История очищена")