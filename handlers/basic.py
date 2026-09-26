import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from handlers.keyboards import main_menu_kb, back_to_main_kb, support_menu_kb
from handlers.faq_search import search_faq, FAQ_DATA

router = Router()

# --- Меню ---
@router.message(F.command.startswith("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот поддержки для будущих мам. Чем могу помочь?", reply_markup=main_menu_kb())

@router.callback_query(F.data == "menu:main")
async def cb_back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu_kb())
    await callback.answer()

@router.callback_query(F.data == "support:menu")
async def cb_support_menu(callback: CallbackQuery):
    await callback.message.edit_text("Выбери, что сейчас ближе:", reply_markup=support_menu_kb())
    await callback.answer()

# --- Поддержка (эмпатические ответы) ---
SUPPORT_RESPONSES = {
    "anxiety": "Тревога сейчас — это нормально. Давай просто подышим пару минут? Или я могу прислать одну очень тёплую фразу.",
    "sleep": "Когда не спится, попробуй просто лежать и не ругать себя за это. Хочешь технику дыхания?",
    "hard": "Сложные дни бывают у всех. Ты не одна. Хочешь просто выговориться текстом, а я побуду тут? Или лучше что-то отвлечённое?",
    "breath": "Техника 4-7-8: вдохни на 4 счёта, задержи дыхание на 7, выдохни на 8. Сделай так 3 раза. Это снижает пульс и тревогу."
}

@router.callback_query(F.data.startswith("support:"))
async def cb_support_category(callback: CallbackQuery):
    category = callback.data.split(":")
    text = SUPPORT_RESPONSES.get(category, "Всё будет хорошо. Если хочешь, можем просто поболтать о чём-нибудь хорошем.")
    await callback.message.edit_text(text, reply_markup=back_to_main_kb())
    await callback.answer()

# --- FAQ Поиск ---
@router.callback_query(F.data == "faq:menu")
async def cb_faq_menu(callback: CallbackQuery):
    await callback.message.edit_text("Напиши свой вопрос текстом, я постараюсь найти ответ в базе знаний (даже если есть опечатки!).", reply_markup=back_to_main_kb())
    await callback.answer()

@router.message(F.text)
async def handle_text_search(message: Message):
    results = search_faq(message.text, threshold=60)
    
    if not results:
        await message.answer("Я не нашла точного ответа. Попробуй перефразировать или нажми «Частые вопросы» в меню.", reply_markup=main_menu_kb())
        return
    
    # Если одно уверенное совпадение (>80) — отвечаем сразу
    if len(results) == 1 and results > 80:
        idx = results
        await message.answer(f"📖 {FAQ_DATA[idx]['answer']}", reply_markup=main_menu_kb())
        return
    
    # Если несколько вариантов — предлагаем кнопки
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    
    for idx, match_text, score in results:
        btn_text = f"{match_text[:30]}... ({score}%)" if len(match_text) > 30 else match_text
        kb.button(text=btn_text, callback_data=f"faq:show:{idx}")
    
    kb.adjust(1)
    # Добавляем кнопку назад
    kb.row(back_to_main_kb().inline_keyboard)
    
    await message.answer("Возможно, ты имел в виду один из этих вопросов:", reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("faq:show:"))
async def cb_faq_show(callback: CallbackQuery):
    idx = int(callback.data.split(":"))
    await callback.message.edit_text(f"📖 {FAQ_DATA[idx]['answer']}", reply_markup=back_to_main_kb())
    await callback.answer()
