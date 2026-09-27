from aiogram import Router, F
from aiogram.types import CallbackQuery

from handlers.storage import prep_items
from handlers.keyboards import prep_checklist_kb

router = Router()

ITEMS = [
    "Оформить декретный отпуск",
    "Оформить обменную карту",
    "Выбрать роддом и врача (если ещё не выбрано)",
    "Оформить родовой сертификат",
    "Купить/подготовить коляску",
    "Купить/подготовить кроватку",
    "Подготовить автокресло",
    "Купить первую одежду для малыша",
    "Продумать место для кормления и пеленания дома",
    "Оформить полис ОМС на будущего малыша (уточнить сроки)",
    "Подготовить документы для больничного/пособий",
    "Договориться с близкими о помощи первые недели",
    "Обсудить с партнёром распределение обязанностей после родов",
    "Заранее продумать питание на первые дни дома (заморозки и т.д.)",
]


def get_text(checked_count: int, total: int) -> str:
    return (
        f"✅ Сделано: {checked_count} из {total}\n\n"
        "Это более долгосрочные дела — не обязательно всё успевать разом, "
        "можно постепенно, в своём темпе. Нажимай на пункт, когда что-то будет готово."
    )


@router.callback_query(F.data == "prep:menu")
async def cb_prep_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    checked = prep_items.setdefault(user_id, set())

    await callback.message.edit_text(
        get_text(len(checked), len(ITEMS)),
        reply_markup=prep_checklist_kb(ITEMS, checked),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prep:toggle:"))
async def cb_prep_toggle(callback: CallbackQuery):
    idx = int(callback.data.split(":")[2])
    user_id = callback.from_user.id
    checked = prep_items.setdefault(user_id, set())

    if idx in checked:
        checked.remove(idx)
    else:
        checked.add(idx)

    await callback.message.edit_text(
        get_text(len(checked), len(ITEMS)),
        reply_markup=prep_checklist_kb(ITEMS, checked),
    )
    await callback.answer()


@router.callback_query(F.data == "prep:reset")
async def cb_prep_reset(callback: CallbackQuery):
    user_id = callback.from_user.id
    prep_items[user_id] = set()

    await callback.message.edit_text(
        get_text(0, len(ITEMS)),
        reply_markup=prep_checklist_kb(ITEMS, set()),
    )
    await callback.answer("Список сброшен")