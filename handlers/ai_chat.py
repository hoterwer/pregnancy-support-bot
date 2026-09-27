import os
import httpx
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.states import ChatStates
from handlers.keyboards import back_to_main_kb

router = Router()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"

SYSTEM_PROMPT = (
    "Ты — тёплый, поддерживающий и эмпатичный собеседник для беременной девушки. "
    "Общайся неформально, на 'ты', с заботой, но без слащавости. "
    "ВАЖНО: собеседница — девушка, поэтому всегда обращайся к ней и говори о ней "
    "в женском роде (например: 'ты почувствовала', 'заметила', 'сказала', а не "
    "мужские окончания вроде 'почувствовал', 'заметил'). Отвечай кратко (2-5 "
    "предложений), если только не просят подробнее.\n\n"
    "СТРОГИЕ ПРАВИЛА БЕЗОПАСНОСТИ:\n"
    "1. Никогда не ставь диагнозы и не утверждай, что что-то точно нормально или опасно "
    "с медицинской точки зрения — вместо этого мягко направляй к врачу.\n"
    "2. Никогда не называй конкретные лекарства, дозировки или схемы приёма.\n"
    "3. Если пользователь описывает тревожные симптомы (сильная боль, кровотечение, "
    "отсутствие шевелений, высокая температура и т.п.) — сразу и прямо посоветуй "
    "немедленно связаться с врачом или скорой, без промедления.\n"
    "4. Если не уверена в фактической информации — честно скажи об этом, не выдумывай.\n"
    "5. Ты не замена врачу, и в сложных вопросах всегда об этом напоминай."
)


async def ask_ai(user_message: str) -> str:
    # .strip() убирает случайные пробелы/переносы строк, которые могли
    # попасть в .env при копировании ключа — частая причина странных ошибок
    api_key = (os.getenv("AI_API_KEY") or "").strip()

    if not api_key:
        return "ИИ пока не подключен — не найден ключ в настройках. Скажи об этом тому, кто настраивал бота 🙈"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)

            # Если что-то пошло не так — печатаем подробности в терминал,
            # чтобы можно было точно понять причину
            if response.status_code != 200:
                print(f"❌ Ошибка ИИ: статус {response.status_code}")
                print(f"Ответ сервера: {response.text}")
                response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Ошибка при запросе к ИИ: {e}")
        return (
            "Не получилось получить ответ от ИИ (возможно, сервер сейчас перегружен — "
            "бесплатные модели иногда с этим сталкиваются). Попробуй ещё раз через минутку 🙏"
        )


@router.callback_query(F.data == "chat:smalltalk")
async def cb_chat_smalltalk(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ChatStates.talking)
    await callback.message.edit_text(
        "Я тут, слушаю 💬 Можешь написать что угодно — как дела, что беспокоит, "
        "или просто поболтать. Чтобы выйти — нажми «В главное меню».",
        reply_markup=back_to_main_kb(),
    )
    await callback.answer()


@router.message(ChatStates.talking)
async def handle_ai_chat(message: Message):
    thinking = await message.answer("Секунду, думаю... 💭")
    reply = await ask_ai(message.text)
    await thinking.delete()
    await message.answer(reply, reply_markup=back_to_main_kb())