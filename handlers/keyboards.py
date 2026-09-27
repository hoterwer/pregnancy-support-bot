from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📖 Частые вопросы", callback_data="faq:menu")
    kb.button(text="💖 Поддержка", callback_data="support:menu")
    kb.button(text="📅 Мой срок", callback_data="tracker:menu")
    kb.button(text="🦶 Шевеления", callback_data="kicks:menu")
    kb.button(text="😊 Настроение", callback_data="mood:menu")
    kb.button(text="🎒 В роддом", callback_data="checklist:menu")
    kb.button(text="⏱ Схватки", callback_data="contractions:menu")
    kb.button(text="💌 Письма малышу", callback_data="letters:menu")
    kb.button(text="🤗 Обнять", callback_data="hug:get")
    kb.button(text="💑 Для партнёра", callback_data="partner:menu")
    kb.button(text="📚 Почитать", callback_data="reading:menu")
    kb.button(text="📋 Вопросы врачу", callback_data="doctorq:menu")
    kb.button(text="✅ Дела до родов", callback_data="prep:menu")
    kb.button(text="🩺 Забота о теле", callback_data="symptoms:menu")
    kb.button(text="🌷 Забота о себе", callback_data="selfcare:menu")
    kb.button(text="☀️ Радость дня", callback_data="joy:get")
    kb.button(text="🔔 Напоминания", callback_data="reminders:menu")
    kb.button(text="💬 Поболтать", callback_data="chat:smalltalk")
    kb.adjust(2, 2, 2, 2, 2, 2, 2, 2, 1)
    return kb.as_markup()


def back_to_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 В главное меню", callback_data="menu:main")
    return kb.as_markup()


def support_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="😣 Мне тревожно", callback_data="support:anxiety")
    kb.button(text="😴 Не могу уснуть", callback_data="support:sleep")
    kb.button(text="😫 Тяжёлый день", callback_data="support:hard")
    kb.button(text="🥺 Одиноко", callback_data="support:lonely")
    kb.button(text="😨 Боюсь родов", callback_data="support:scared")
    kb.button(text="🥱 Устала физически", callback_data="support:tired")
    kb.button(text="🌬 Дыхание 4-7-8", callback_data="support:breath")
    kb.button(text="🌸 Слово поддержки", callback_data="support:affirmation")
    kb.button(text="🔙 Назад", callback_data="menu:main")
    kb.adjust(2, 2, 2, 2, 1)
    return kb.as_markup()


def tracker_result_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Изменить дату", callback_data="tracker:reset")
    kb.button(text="🔙 В главное меню", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def kicks_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Отметить шевеление", callback_data="kicks:add")
    kb.button(text="📜 История по дням", callback_data="kicks:history")
    kb.button(text="🔄 Обнулить счётчик", callback_data="kicks:reset")
    kb.button(text="🔙 В главное меню", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def mood_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="😊 Хорошо", callback_data="mood:set:good")
    kb.button(text="😐 Нормально", callback_data="mood:set:neutral")
    kb.button(text="😢 Тяжело", callback_data="mood:set:hard")
    kb.button(text="📜 История", callback_data="mood:history")
    kb.button(text="🔙 В главное меню", callback_data="menu:main")
    kb.adjust(3, 1, 1)
    return kb.as_markup()


def mood_note_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✍️ Да, добавить", callback_data="mood:note:yes")
    kb.button(text="Нет, просто так", callback_data="mood:note:no")
    kb.adjust(1)
    return kb.as_markup()


def checklist_kb(items: list[str], checked: set):
    kb = InlineKeyboardBuilder()
    for idx, item in enumerate(items):
        prefix = "✅" if idx in checked else "⬜"
        kb.button(text=f"{prefix} {item}", callback_data=f"checklist:toggle:{idx}")
    kb.button(text="🔄 Сбросить всё", callback_data="checklist:reset")
    kb.button(text="🔙 В главное меню", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def contractions_menu_kb(active: bool):
    kb = InlineKeyboardBuilder()
    if active:
        kb.button(text="⏹ Закончить схватку", callback_data="contractions:stop")
    else:
        kb.button(text="▶️ Начать схватку", callback_data="contractions:start")
    kb.button(text="🔄 Сбросить историю", callback_data="contractions:reset")
    kb.button(text="🔙 В главное меню", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def letters_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✍️ Написать письмо", callback_data="letters:write")
    kb.button(text="📖 Читать письма", callback_data="letters:read:0")
    kb.button(text="🔙 В главное меню", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def letters_read_kb(index: int, total: int):
    kb = InlineKeyboardBuilder()
    if index > 0:
        kb.button(text="⬅️ Предыдущее", callback_data=f"letters:read:{index - 1}")
    if index < total - 1:
        kb.button(text="➡️ Следующее", callback_data=f"letters:read:{index + 1}")
    kb.adjust(2)
    kb.button(text="🔙 К письмам", callback_data="letters:menu")
    kb.adjust(2, 1)
    return kb.as_markup()


def doctor_questions_kb(questions: list):
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Добавить вопрос", callback_data="doctorq:add")

    for idx, q in enumerate(questions):
        prefix = "✅" if q["asked"] else "⬜"
        label = q["text"][:35] + "..." if len(q["text"]) > 35 else q["text"]
        kb.button(text=f"{prefix} {label}", callback_data=f"doctorq:toggle:{idx}")

    if questions:
        kb.button(text="🗑 Очистить отмеченные", callback_data="doctorq:clear_asked")
        kb.button(text="🔄 Очистить всё", callback_data="doctorq:clear_all")

    kb.button(text="🔙 В главное меню", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def prep_checklist_kb(items: list[str], checked: set):
    kb = InlineKeyboardBuilder()
    for idx, item in enumerate(items):
        prefix = "✅" if idx in checked else "⬜"
        kb.button(text=f"{prefix} {item}", callback_data=f"prep:toggle:{idx}")
    kb.button(text="🔄 Сбросить всё", callback_data="prep:reset")
    kb.button(text="🔙 В главное меню", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def symptoms_menu_kb(symptoms_dict: dict, selected: set):
    kb = InlineKeyboardBuilder()
    for key, (label, _tip) in symptoms_dict.items():
        prefix = "✅" if key in selected else "⬜"
        kb.button(text=f"{prefix} {label}", callback_data=f"symptoms:toggle:{key}")
    kb.adjust(2)
    kb.button(text="📜 История", callback_data="symptoms:history")
    kb.button(text="🔙 В главное меню", callback_data="menu:main")
    kb.adjust(2, 1, 1)
    return kb.as_markup()


def selfcare_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🌸 Восстановление после родов", callback_data="selfcare:topic:recovery")
    kb.button(text="🤱 Основы ГВ", callback_data="selfcare:topic:breastfeeding")
    kb.button(text="🌙 Первые недели с малышом", callback_data="selfcare:topic:early_weeks")
    kb.button(text="💛 Ты остаёшься собой", callback_data="selfcare:topic:identity")
    kb.button(text="🔙 В главное меню", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def reminders_menu_kb(data: dict):
    kb = InlineKeyboardBuilder()

    water_status = "✅ Вкл" if data["water"]["enabled"] else "⬜ Выкл"
    kb.button(text=f"💧 Вода: {water_status}", callback_data="reminders:toggle_water")

    if data["vitamins"]["time"]:
        vit_status = "✅ Вкл" if data["vitamins"]["enabled"] else "⬜ Выкл"
        kb.button(
            text=f"💊 Витамины ({data['vitamins']['time']}): {vit_status}",
            callback_data="reminders:toggle_vitamins",
        )
    else:
        kb.button(text="💊 Настроить напоминание про витамины", callback_data="reminders:set_vitamins_time")

    for item in data["custom"]:
        status = "✅" if item["enabled"] else "⬜"
        label = item["text"][:25] + "..." if len(item["text"]) > 25 else item["text"]
        kb.button(text=f"{status} {label}", callback_data=f"reminders:toggle_custom:{item['id']}")
        kb.button(text=f"🗑 Удалить «{label}»", callback_data=f"reminders:delete_custom:{item['id']}")

    if len(data["custom"]) < 5:
        kb.button(text="➕ Добавить своё напоминание", callback_data="reminders:add_custom")

    kb.button(text="🔙 В главное меню", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()