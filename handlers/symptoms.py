from datetime import date
from aiogram import Router, F
from aiogram.types import CallbackQuery

from handlers.storage import symptoms_today, symptoms_history
from handlers.keyboards import symptoms_menu_kb

router = Router()

# ключ: (название для кнопки, короткий совет)
SYMPTOMS = {
    "edema": ("Отёки", "Попробуй почаще приподнимать ноги повыше уровня сердца и не забывай пить воду — отёки часто усиливаются как раз от нехватки жидкости. Если отёки резко нарастают или появляются на лице — стоит сказать об этом врачу."),
    "heartburn": ("Изжога", "Попробуй есть небольшими порциями и не ложиться сразу после еды. Иногда помогает приподнятое изголовье во время сна."),
    "back_pain": ("Боль в спине", "Тёплый (не горячий) компресс на поясницу и лёгкая растяжка могут помочь. Если удобно — попробуй спать с подушкой между колен."),
    "cramps": ("Судороги", "Часто помогает лёгкая растяжка икр перед сном и достаточное количество жидкости и магния в питании — но лучше уточнить у врача, не нужно ли что-то добавить."),
    "dizziness": ("Головокружение", "Старайся не вставать резко, особенно из положения лёжа. Если кружится голова — присядь и переведи дыхание. Частые эпизоды — повод сказать врачу."),
    "insomnia": ("Бессонница", "Не ругай себя за это — тело просто ищет удобное положение. Попробуй технику дыхания 4-7-8 из раздела «Поддержка»."),
    "nausea": ("Тошнота", "Попробуй есть чаще, но маленькими порциями, и держать под рукой что-то нейтральное вроде крекеров. Имбирный чай тоже часто помогает."),
    "fatigue": ("Усталость", "Это нормально — тело сейчас работает на полную. Разреши себе отдыхать без чувства вины, даже если план на день не выполнен."),
}


def _ensure_today(user_id: int) -> dict:
    today = date.today()
    entry = symptoms_today.get(user_id)

    if entry and entry["date"] != today:
        history = symptoms_history.setdefault(user_id, [])
        history.append({"date": entry["date"], "symptoms": entry["symptoms"]})
        symptoms_today[user_id] = {"date": today, "symptoms": set()}
    elif not entry:
        symptoms_today[user_id] = {"date": today, "symptoms": set()}

    return symptoms_today[user_id]


def get_text(selected: set) -> str:
    if not selected:
        return (
            "🩺 Отметь, что беспокоит сегодня — покажу короткие советы по каждому "
            "пункту. Это не заменяет консультацию врача, но может немного помочь "
            "прямо сейчас."
        )

    tips = "\n\n".join(f"• {SYMPTOMS[key][0]}: {SYMPTOMS[key][1]}" for key in selected)
    return f"🩺 Сегодня отмечено:\n\n{tips}"


@router.callback_query(F.data == "symptoms:menu")
async def cb_symptoms_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    entry = _ensure_today(user_id)

    await callback.message.edit_text(
        get_text(entry["symptoms"]),
        reply_markup=symptoms_menu_kb(SYMPTOMS, entry["symptoms"]),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("symptoms:toggle:"))
async def cb_symptoms_toggle(callback: CallbackQuery):
    key = callback.data.split(":")[2]
    user_id = callback.from_user.id
    entry = _ensure_today(user_id)

    if key in entry["symptoms"]:
        entry["symptoms"].remove(key)
    else:
        entry["symptoms"].add(key)

    await callback.message.edit_text(
        get_text(entry["symptoms"]),
        reply_markup=symptoms_menu_kb(SYMPTOMS, entry["symptoms"]),
    )
    await callback.answer()


@router.callback_query(F.data == "symptoms:history")
async def cb_symptoms_history(callback: CallbackQuery):
    user_id = callback.from_user.id
    today_entry = _ensure_today(user_id)
    history = symptoms_history.get(user_id, [])

    all_entries = history + [today_entry]
    last_entries = [e for e in all_entries if e["symptoms"]][-7:][::-1]

    if not last_entries:
        text = "Пока нет записей с отмеченными симптомами."
    else:
        lines = ["📜 Последние дни:\n"]
        for entry in last_entries:
            date_str = entry["date"].strftime("%d.%m")
            suffix = " (сегодня)" if entry["date"] == date.today() else ""
            names = ", ".join(SYMPTOMS[k][0] for k in entry["symptoms"])
            lines.append(f"{date_str}{suffix} — {names}")
        text = "\n".join(lines)

    await callback.message.edit_text(
        text, reply_markup=symptoms_menu_kb(SYMPTOMS, today_entry["symptoms"])
    )
    await callback.answer()