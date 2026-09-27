from datetime import date
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.states import LetterStates
from handlers.storage import letters
from handlers.keyboards import letters_menu_kb, letters_read_kb, back_to_main_kb

router = Router()


@router.callback_query(F.data == "letters:menu")
async def cb_letters_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    count = len(letters.get(user_id, []))

    text = (
        f"💌 У тебя сохранено писем: {count}\n\n"
        "Можешь написать малышу что угодно — мысли, чувства, пожелания. "
        "Всё сохранится с датой, и потом можно будет перечитать."
    )
    await callback.message.edit_text(text, reply_markup=letters_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "letters:write")
async def cb_letters_write(callback: CallbackQuery, state: FSMContext):
    await state.set_state(LetterStates.waiting_for_letter)
    await callback.message.edit_text(
        "Напиши своё письмо малышу — я всё сохраню 💛"
    )
    await callback.answer()


@router.message(LetterStates.waiting_for_letter)
async def process_letter(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_letters = letters.setdefault(user_id, [])
    user_letters.append({"date": date.today(), "text": message.text})

    await state.clear()
    await message.answer(
        "Письмо сохранено 💌 Когда-нибудь будет так трогательно перечитать это вместе с малышом.",
        reply_markup=back_to_main_kb(),
    )


@router.callback_query(F.data.startswith("letters:read:"))
async def cb_letters_read(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_letters = letters.get(user_id, [])

    if not user_letters:
        await callback.message.edit_text(
            "Пока нет ни одного письма. Самое время написать первое! 💌",
            reply_markup=letters_menu_kb(),
        )
        await callback.answer()
        return

    index = int(callback.data.split(":")[2])
    index = max(0, min(index, len(user_letters) - 1))

    letter = user_letters[index]
    date_str = letter["date"].strftime("%d.%m.%Y")

    text = (
        f"💌 Письмо от {date_str} ({index + 1} из {len(user_letters)})\n\n"
        f"{letter['text']}"
    )

    await callback.message.edit_text(
        text, reply_markup=letters_read_kb(index, len(user_letters))
    )
    await callback.answer()