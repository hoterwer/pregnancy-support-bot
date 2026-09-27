from datetime import datetime, date
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.states import TrackerStates
from handlers.storage import due_dates
from handlers.keyboards import back_to_main_kb, tracker_result_kb
from handlers.size_comparisons import get_size_comparison
from handlers.weekly_info import get_weekly_fact, get_milestone

router = Router()

TOTAL_PREGNANCY_DAYS = 280  # 40 недель


@router.callback_query(F.data == "tracker:menu")
async def cb_tracker_menu(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    if user_id in due_dates:
        await show_current_week(callback.message, user_id)
    else:
        await callback.message.edit_text(
            "Напиши, пожалуйста, предполагаемую дату родов (ПДР) в формате ДД.ММ.ГГГГ.\n\n"
            "Например: 15.03.2027\n\n"
            "Если не знаешь точную дату — можно посмотреть в обменной карте или спросить у врача.",
            reply_markup=back_to_main_kb(),
        )
        await state.set_state(TrackerStates.waiting_for_due_date)

    await callback.answer()


@router.callback_query(F.data == "tracker:reset")
async def cb_tracker_reset(callback: CallbackQuery, state: FSMContext):
    due_dates.pop(callback.from_user.id, None)
    await callback.message.edit_text(
        "Хорошо, давай обновим! Напиши предполагаемую дату родов в формате ДД.ММ.ГГГГ.",
        reply_markup=back_to_main_kb(),
    )
    await state.set_state(TrackerStates.waiting_for_due_date)
    await callback.answer()


@router.message(TrackerStates.waiting_for_due_date)
async def process_due_date(message: Message, state: FSMContext):
    try:
        due_date = datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except ValueError:
        await message.answer(
            "Хм, не могу понять эту дату 🙈 Попробуй в формате ДД.ММ.ГГГГ, например: 15.03.2027"
        )
        return

    due_dates[message.from_user.id] = due_date
    await state.clear()
    await show_current_week(message, message.from_user.id)


async def show_current_week(message: Message, user_id: int):
    due_date = due_dates[user_id]
    days_left = (due_date - date.today()).days
    days_pregnant = TOTAL_PREGNANCY_DAYS - days_left
    current_week = days_pregnant // 7

    if days_left < 0:
        text = (
            "Судя по указанной дате, срок родов уже прошёл 💕 "
            "Если данные устарели — нажми «🔄 Изменить дату»."
        )
    elif current_week < 1:
        text = "Похоже, по этой дате беременность ещё не началась. Проверь, пожалуйста, дату — нажми «🔄 Изменить дату»."
    else:
        text = (
            f"Сейчас примерно {current_week}-я неделя беременности 🤰\n"
            f"До предполагаемой даты родов осталось около {days_left} дней."
        )

        comparison = get_size_comparison(current_week)
        if comparison:
            fruit, animal = comparison
            text += (
                f"\n\n🍓 Малыш сейчас размером примерно как {fruit}, "
                f"а по размеру похож на {animal} — вот такой маленький и уже такой большой! 💕"
            )

        milestone = get_milestone(current_week)
        if milestone:
            text += f"\n\n🎉 {milestone}"

        next_fact = get_weekly_fact(current_week + 1)
        if next_fact:
            text += f"\n\n👀 На {current_week + 1}-й неделе: {next_fact}."

        text += "\n\nЭто приблизительный расчёт, точный срок лучше уточнять у врача."

    await message.answer(text, reply_markup=tracker_result_kb())