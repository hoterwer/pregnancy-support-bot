import random
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from handlers.keyboards import main_menu_kb, back_to_main_kb, support_menu_kb
from handlers.faq_search import search_faq, FAQ_DATA
from handlers.ai_chat import ask_ai
from handlers.states import NameStates
from handlers.storage import user_names

router = Router()


def greeting_menu_text(user_id: int) -> str:
    name = user_names.get(user_id)
    if name:
        return f"Привет, {name}! Чем могу помочь?"
    return "Привет! Чем могу помочь?"


# --- Меню ---
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    if user_id in user_names:
        await message.answer(greeting_menu_text(user_id), reply_markup=main_menu_kb())
    else:
        await state.set_state(NameStates.waiting_for_name)
        await message.answer(
            "Привет! Я бот поддержки для будущих мам 💛\n\n"
            "Для начала — как тебя зовут?"
        )


@router.message(NameStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    user_names[message.from_user.id] = name
    await state.clear()

    await message.answer(
        f"Очень приятно, {name}! 💛 Буду рядом на протяжении всего пути.",
        reply_markup=main_menu_kb(),
    )


@router.callback_query(F.data == "menu:main")
async def cb_back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        f"Главное меню:", reply_markup=main_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "support:menu")
async def cb_support_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выбери, что сейчас ближе:", reply_markup=support_menu_kb()
    )
    await callback.answer()


# --- Поддержка (эмпатические ответы) ---
SUPPORT_RESPONSES = {
    "anxiety": (
        "Тревога сейчас — это очень по-человечески. Тело меняется, внутри растёт "
        "целая жизнь, и разум просто пытается всё контролировать, хотя контролировать "
        "тут особо нечего — и это нормально отпустить.\n\n"
        "Попробуй на пару минут просто сосредоточиться на дыхании — вдох, выдох, без "
        "спешки. Ты не обязана сейчас ничего решать или с чем-то справляться. Просто побудь."
    ),
    "sleep": (
        "Бессонница на этом этапе — частый спутник, и это не значит, что с тобой "
        "что-то не так. Тело просто ищет удобное положение, а мысли не хотят "
        "останавливаться.\n\n"
        "Не заставляй себя уснуть силой — попробуй просто полежать в темноте, ни за "
        "что себя не ругая. Если хочется — включи технику дыхания, она помогает "
        "немного отпустить напряжение."
    ),
    "hard": (
        "Сложные дни случаются у всех, даже если со стороны кажется, что у других "
        "всё легко и гладко. Ты имеешь полное право устать, разозлиться или просто "
        "расклеиться — это не слабость, это часть пути.\n\n"
        "Хочешь — выговорись мне текстом, я просто побуду рядом и послушаю, без "
        "советов и оценок. А если сейчас хочется отвлечься — можем просто поболтать "
        "о чём-нибудь хорошем."
    ),
    "lonely": (
        "Одиночество иногда накрывает даже тогда, когда рядом есть близкие — просто "
        "потому что то, что происходит внутри тебя, никто не может прочувствовать "
        "так же, как ты.\n\n"
        "Это чувство не означает, что с тобой или с твоими отношениями что-то не "
        "так. Если есть кому позвонить прямо сейчас — не стесняйся. А если хочется "
        "просто выговориться — я тут, никуда не тороплюсь."
    ),
    "scared": (
        "Бояться родов — это абсолютно нормально, даже если это не первая "
        "беременность. Неизвестность вообще пугает, а тут ещё и что-то настолько "
        "важное.\n\n"
        "Помни: рядом будут врачи, которые через это проходили сотни раз, и твоё "
        "тело умеет гораздо больше, чем кажется. Если тревога сильная — можно "
        "обсудить её со своим врачом заранее, это совершенно нормальный вопрос "
        "для консультации."
    ),
    "tired": (
        "Физическая усталость на этом сроке — это не про лень, это тело реально "
        "работает на пределе, растя целого человека. Имеешь полное право прилечь, "
        "отменить планы и ничего не делать сегодня.\n\n"
        "Постарайся сейчас не сравнивать себя с тем, сколько успевала раньше — "
        "сейчас другой этап, и заботиться о себе так же важно, как заботиться о малыше."
    ),
    "breath": (
        "Вот простая техника, которая помогает снизить тревогу и немного "
        "успокоить пульс — 4-7-8:\n\n"
        "Вдохни через нос на 4 счёта → задержи дыхание на 7 счётов → выдохни через "
        "рот на 8 счётов. Повтори 3-4 раза, не спеша.\n\n"
        "Если голова слегка закружится — это нормально, просто вернись к обычному "
        "дыханию и попробуй ещё раз чуть позже."
    ),
}


@router.callback_query(F.data == "support:affirmation")
async def cb_support_affirmation(callback: CallbackQuery):
    phrase = random.choice(FAQ_DATA["affirmations"])
    await callback.message.edit_text(f"🌸 {phrase}", reply_markup=back_to_main_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("support:"))
async def cb_support_category(callback: CallbackQuery):
    category = callback.data.split(":")[1]
    text = SUPPORT_RESPONSES.get(
        category, "Всё будет хорошо. Если хочешь, можем просто поболтать о чём-нибудь хорошем."
    )
    await callback.message.edit_text(text, reply_markup=back_to_main_kb())
    await callback.answer()


# --- FAQ Поиск ---
@router.callback_query(F.data == "faq:menu")
async def cb_faq_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Напиши свой вопрос текстом, я постараюсь найти ответ в базе знаний (даже если есть опечатки!).",
        reply_markup=back_to_main_kb(),
    )
    await callback.answer()


@router.message(F.text)
async def handle_text_search(message: Message):
    results = search_faq(message.text, threshold=70)

    if results and results[0][2] > 85:
        idx = results[0][0]
        await message.answer(
            f"📖 {FAQ_DATA['faq'][idx]['answer']}",
            reply_markup=main_menu_kb(),
        )
        return

    thinking = await message.answer("Секунду, думаю... 💭")
    reply = await ask_ai(message.text)
    await thinking.delete()
    await message.answer(reply, reply_markup=main_menu_kb())


@router.callback_query(F.data.startswith("faq:show:"))
async def cb_faq_show(callback: CallbackQuery):
    idx = int(callback.data.split(":")[2])
    await callback.message.edit_text(
        f"📖 {FAQ_DATA['faq'][idx]['answer']}",
        reply_markup=back_to_main_kb(),
    )
    await callback.answer()