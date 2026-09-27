from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.states import DoctorQuestionStates
from handlers.storage import doctor_questions
from handlers.keyboards import doctor_questions_kb

router = Router()


def get_text(questions: list) -> str:
    if not questions:
        return (
            "📋 Здесь можно копить вопросы для врача — записывай, как только что-то "
            "приходит в голову, а на приёме уже не придётся ничего судорожно вспоминать.\n\n"
            "Пока список пуст — нажми «➕ Добавить вопрос»."
        )

    asked_count = sum(1 for q in questions if q["asked"])
    return (
        f"📋 Вопросов в списке: {len(questions)} (отмечено как заданные: {asked_count})\n\n"
        "Нажимай на вопрос, чтобы отметить его как заданный."
    )


@router.callback_query(F.data == "doctorq:menu")
async def cb_doctorq_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    questions = doctor_questions.setdefault(user_id, [])

    await callback.message.edit_text(
        get_text(questions), reply_markup=doctor_questions_kb(questions)
    )
    await callback.answer()


@router.callback_query(F.data == "doctorq:add")
async def cb_doctorq_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DoctorQuestionStates.waiting_for_question)
    await callback.message.edit_text(
        "Напиши вопрос, который хочешь задать врачу — я его сохраню 📋"
    )
    await callback.answer()


@router.message(DoctorQuestionStates.waiting_for_question)
async def process_doctor_question(message: Message, state: FSMContext):
    user_id = message.from_user.id
    questions = doctor_questions.setdefault(user_id, [])
    questions.append({"text": message.text, "asked": False})

    await state.clear()
    await message.answer(
        "Записала! 💛", reply_markup=doctor_questions_kb(questions)
    )


@router.callback_query(F.data.startswith("doctorq:toggle:"))
async def cb_doctorq_toggle(callback: CallbackQuery):
    idx = int(callback.data.split(":")[2])
    user_id = callback.from_user.id
    questions = doctor_questions.setdefault(user_id, [])

    if 0 <= idx < len(questions):
        questions[idx]["asked"] = not questions[idx]["asked"]

    await callback.message.edit_text(
        get_text(questions), reply_markup=doctor_questions_kb(questions)
    )
    await callback.answer()


@router.callback_query(F.data == "doctorq:clear_asked")
async def cb_doctorq_clear_asked(callback: CallbackQuery):
    user_id = callback.from_user.id
    questions = doctor_questions.get(user_id, [])
    remaining = [q for q in questions if not q["asked"]]
    doctor_questions[user_id] = remaining

    await callback.message.edit_text(
        get_text(remaining), reply_markup=doctor_questions_kb(remaining)
    )
    await callback.answer("Заданные вопросы убраны")


@router.callback_query(F.data == "doctorq:clear_all")
async def cb_doctorq_clear_all(callback: CallbackQuery):
    user_id = callback.from_user.id
    doctor_questions[user_id] = []

    await callback.message.edit_text(
        get_text([]), reply_markup=doctor_questions_kb([])
    )
    await callback.answer("Список очищен")