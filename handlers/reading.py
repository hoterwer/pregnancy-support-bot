import os
from datetime import date
import httpx
from aiogram import Router, F
from aiogram.types import CallbackQuery

from handlers.storage import due_dates
from handlers.keyboards import back_to_main_kb
from handlers.ai_chat import OPENROUTER_URL, MODEL

router = Router()

TOTAL_PREGNANCY_DAYS = 280

READING_SYSTEM_PROMPT = (
    "Ты — помощник, который подбирает материалы для чтения под конкретную неделю "
    "беременности. Обращайся в женском роде. Отвечай СТРОГО в этом формате:\n\n"
    "📚 Книги:\n"
    "1. [Название] — [Автор]. [Одна строка о пользе именно сейчас]\n"
    "2. ...\n"
    "3. ...\n\n"
    "📰 Темы для поиска:\n"
    "1. [конкретная тема или вопрос]\n"
    "2. ...\n"
    "3. ...\n"
    "4. ...\n"
    "5. ...\n\n"
    "ВАЖНЫЕ ПРАВИЛА:\n"
    "- В разделе «Книги» указывай ТОЛЬКО реально существующие, известные книги "
    "о беременности и материнстве вместе с настоящими авторами. Никогда не "
    "выдумывай название или автора, если не уверена, что книга существует.\n"
    "- В разделе «Темы для поиска» НЕ придумывай конкретные статьи, издания, "
    "ссылки или авторов статей — формулируй только саму тему или вопрос, "
    "который стоит самостоятельно поискать и почитать.\n"
    "- Темы и книги должны быть релевантны именно указанной неделе беременности."
)


async def get_reading_list(week: int) -> str:
    api_key = (os.getenv("AI_API_KEY") or "").strip()

    if not api_key:
        return "ИИ пока не подключен — не найден ключ в настройках."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": READING_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Сейчас {week}-я неделя беременности. Подбери книги и темы для чтения.",
            },
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            if response.status_code != 200:
                print(f"❌ Ошибка подборки чтения: статус {response.status_code}")
                print(f"Ответ сервера: {response.text}")
                response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Ошибка при получении подборки чтения: {e}")
        return "Не получилось собрать подборку — сервер сейчас перегружен. Попробуй ещё раз через минутку 🙏"


@router.callback_query(F.data == "reading:menu")
async def cb_reading_menu(callback: CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in due_dates:
        await callback.message.edit_text(
            "Чтобы подобрать подборку под твой срок, сначала укажи предполагаемую "
            "дату родов в разделе «📅 Мой срок».",
            reply_markup=back_to_main_kb(),
        )
        await callback.answer()
        return

    due_date = due_dates[user_id]
    days_left = (due_date - date.today()).days
    days_pregnant = TOTAL_PREGNANCY_DAYS - days_left
    current_week = max(1, days_pregnant // 7)

    await callback.message.edit_text("Подбираю подборку под твой срок... 💭")
    reading_list = await get_reading_list(current_week)

    text = f"📚 Подборка для {current_week}-й недели:\n\n{reading_list}"
    await callback.message.edit_text(text, reply_markup=back_to_main_kb())
    await callback.answer()