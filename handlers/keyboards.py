from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📖 Частые вопросы", callback_data="faq:menu")
    kb.button(text="💖 Поддержка", callback_data="support:menu")
    kb.button(text="📅 Мой срок", callback_data="tracker:menu")
    kb.button(text="🦶 Шевеления", callback_data="kicks:menu")
    kb.button(text="💬 Поболтать", callback_data="chat:smalltalk")
    kb.adjust(2, 2, 1)
    return kb.as_markup()

def back_to_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 В главное меню", callback_data="menu:main")
    return kb.as_markup()

def support_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="😣 Мне тревожно", callback_data="support:anxiety")
    kb.button(text="😴 Не могу уснуть", callback_data="support:sleep")
    kb.button(text="😫 Сложный день", callback_data="support:hard")
    kb.button(text="🌬 Дыхание 4-7-8", callback_data="support:breath")
    kb.button(text="🔙 Назад", callback_data="menu:main")
    kb.adjust(2, 2, 1)
    return kb.as_markup()
