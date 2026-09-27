from aiogram import Router, F
from aiogram.types import CallbackQuery

from handlers.storage import packed_items
from handlers.keyboards import checklist_kb

router = Router()

ITEMS = [
    "Паспорт и полис ОМС",
    "Обменная карта",
    "Родовой сертификат (если есть)",
    "Телефон и зарядка",
    "Удобная одежда для роддома",
    "Халат и тапочки",
    "Носки тёплые",
    "Нижнее бельё (несколько пар)",
    "Прокладки послеродовые",
    "Гигиенические принадлежности",
    "Бутылка воды",
    "Перекус для мамы",
    "Одежда для малыша на выписку",
    "Подгузники для новорождённого",
    "Плед или конверт на выписку",
    "Средства для кормления (если планируется)",
]


def get_text(checked_count: int, total: int) -> str:
    return (
        f"🎒 Собрано: {checked_count} из {total}\n\n"
        "Нажимай на пункт, чтобы отметить его как собранный."
    )


@router.callback_query(F.data == "checklist:menu")
async def cb_checklist_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    checked = packed_items.setdefault(user_id, set())

    await callback.message.edit_text(
        get_text(len(checked), len(ITEMS)),
        reply_markup=checklist_kb(ITEMS, checked),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("checklist:toggle:"))
async def cb_checklist_toggle(callback: CallbackQuery):
    idx = int(callback.data.split(":")[2])
    user_id = callback.from_user.id
    checked = packed_items.setdefault(user_id, set())

    if idx in checked:
        checked.remove(idx)
    else:
        checked.add(idx)

    await callback.message.edit_text(
        get_text(len(checked), len(ITEMS)),
        reply_markup=checklist_kb(ITEMS, checked),
    )
    await callback.answer()


@router.callback_query(F.data == "checklist:reset")
async def cb_checklist_reset(callback: CallbackQuery):
    user_id = callback.from_user.id
    packed_items[user_id] = set()

    await callback.message.edit_text(
        get_text(0, len(ITEMS)),
        reply_markup=checklist_kb(ITEMS, set()),
    )
    await callback.answer("Список сброшен")