from datetime import date
from aiogram import Router, F
from aiogram.types import CallbackQuery

from handlers.storage import due_dates
from handlers.keyboards import back_to_main_kb

router = Router()

TOTAL_PREGNANCY_DAYS = 280

# Советы партнёру по этапам беременности
TIPS_BY_STAGE = {
    (1, 12): [
        "Первый триместр часто самый тяжёлый физически — токсикоз, усталость, перепады настроения. Это не каприз, это гормоны.",
        "Помогай с бытом без напоминаний — сейчас особенно ценно не создавать лишнюю нагрузку.",
        "Если хочется резких запахов избегать — не спорь, просто прими это как есть.",
    ],
    (13, 27): [
        "Обычно становится полегче — но спина и ноги начинают уставать больше. Массаж стоп — маленький, но действенный жест.",
        "Скоро появятся первые шевеления — это очень трогательный момент, будь рядом, когда она захочет поделиться.",
        "Поддержи с активностью: совместные неспешные прогулки — и полезно, и время вместе.",
    ],
    (28, 36): [
        "Живот уже большой, обычное становится сложным — завязать шнурки, встать с кровати. Помогай физически, без просьб.",
        "Может появиться тревога перед родами — это нормально. Просто слушай, не обязательно решать проблему.",
        "Начните вместе собирать сумку в роддом — так спокойнее обоим.",
    ],
    (37, 42): [
        "Роды могут начаться в любой момент — держи телефон заряженным и будь на связи.",
        "Уточните заранее маршрут до роддома и все документы — чтобы в нужный момент не искать их в панике.",
        "Сейчас как никогда важно просто быть рядом и сохранять спокойствие — она чувствует твоё состояние.",
    ],
}


def get_tips_for_week(week: int):
    for (start, end), tips in TIPS_BY_STAGE.items():
        if start <= week <= end:
            return tips
    return None


@router.callback_query(F.data == "partner:menu")
async def cb_partner_menu(callback: CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in due_dates:
        await callback.message.edit_text(
            "Чтобы показать актуальные советы, сначала нужно указать предполагаемую "
            "дату родов в разделе «📅 Мой срок».",
            reply_markup=back_to_main_kb(),
        )
        await callback.answer()
        return

    due_date = due_dates[user_id]
    days_left = (due_date - date.today()).days
    days_pregnant = TOTAL_PREGNANCY_DAYS - days_left
    current_week = max(1, days_pregnant // 7)

    tips = get_tips_for_week(current_week)

    if not tips:
        text = "Сейчас особенных подсказок для этого срока нет — просто будь рядом 💛"
    else:
        tips_text = "\n\n".join(f"• {tip}" for tip in tips)
        text = f"💑 Сейчас примерно {current_week}-я неделя. Вот, что может пригодиться:\n\n{tips_text}"

    await callback.message.edit_text(text, reply_markup=back_to_main_kb())
    await callback.answer()