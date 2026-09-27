from datetime import date
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.states import MoodStates
from handlers.storage import mood_entries
from handlers.keyboards import mood_menu_kb, mood_note_kb, back_to_main_kb

router = Router()

MOOD_LABELS = {
    "good": "😊 Хорошо",
    "neutral": "😐 Нормально",
    "hard": "😢 Тяжело",
}


@router.callback_query(F.data == "mood:menu")
async def cb_mood_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Как ты сегодня? Отметь настроение — это поможет замечать, как меняется самочувствие день ото дня.",
        reply_markup=mood_menu_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("mood:set:"))
async def cb_mood_set(callback: CallbackQuery):
    mood_key = callback.data.split(":")[2]
    user_id = callback.from_user.id

    entries = mood_entries.setdefault(user_id, [])
    entries.append({"date": date.today(), "mood": mood_key, "note": None})

    await callback.message.edit_text(
        f"Записала: {MOOD_LABELS[mood_key]}. Хочешь добавить пару слов о том, как прошёл день?",
        reply_markup=mood_note_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "mood:note:yes")
async def cb_mood_note_yes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MoodStates.waiting_for_note)
    await callback.message.edit_text("Напиши, что на душе — я просто послушаю 💛")
    await callback.answer()


@router.callback_query(F.data == "mood:note:no")
async def cb_mood_note_no(callback: CallbackQuery):
    await callback.message.edit_text(
        "Хорошо, записала без заметки. Спасибо, что делишься 💛",
        reply_markup=back_to_main_kb(),
    )
    await callback.answer()


@router.message(MoodStates.waiting_for_note)
async def process_mood_note(message: Message, state: FSMContext):
    user_id = message.from_user.id
    entries = mood_entries.get(user_id, [])

    if entries:
        entries[-1]["note"] = message.text

    await state.clear()
    await message.answer(
        "Спасибо, что рассказала. Я всё сохранила 💛",
        reply_markup=back_to_main_kb(),
    )


@router.callback_query(F.data == "mood:history")
async def cb_mood_history(callback: CallbackQuery):
    user_id = callback.from_user.id
    entries = mood_entries.get(user_id, [])

    if not entries:
        await callback.message.edit_text(
            "Пока нет ни одной записи. Отметь своё настроение, и здесь появится история!",
            reply_markup=mood_menu_kb(),
        )
        await callback.answer()
        return

    last_entries = entries[-7:][::-1]
    lines = ["📜 Последние записи:\n"]
    for entry in last_entries:
        date_str = entry["date"].strftime("%d.%m")
        line = f"{date_str} — {MOOD_LABELS[entry['mood']]}"
        if entry["note"]:
            line += f"\n   💬 {entry['note']}"
        lines.append(line)

    await callback.message.edit_text("\n".join(lines), reply_markup=mood_menu_kb())
    await callback.answer()