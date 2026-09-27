import re
import uuid
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.states import ReminderStates
from handlers.storage import reminders_data
from handlers.keyboards import reminders_menu_kb
from handlers.reminder_scheduler import schedule_interval, schedule_daily, unschedule

router = Router()

WATER_TEXT = "💧 Не забудь попить воды — это важно и для тебя, и для малыша."
TIME_PATTERN = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


def _ensure_user_data(user_id: int) -> dict:
    if user_id not in reminders_data:
        reminders_data[user_id] = {
            "water": {"enabled": True, "interval_minutes": 120},
            "vitamins": {"enabled": False, "time": None},
            "custom": [],
        }
        # Напоминание про воду включаем сразу по умолчанию
        schedule_interval(f"water:{user_id}", user_id, WATER_TEXT, 120, active_hours=(8, 22))
    return reminders_data[user_id]


MENU_TEXT = (
    "🔔 Напоминания\n\n"
    "Здесь можно включать и выключать стандартные напоминания и добавлять свои "
    "(до 5 штук) — например, про лекарства или что-то ещё важное в течение дня. "
    "Напоминания приходят только с 8:00 до 22:00, чтобы не будить ночью."
)


@router.callback_query(F.data == "reminders:menu")
async def cb_reminders_menu(callback: CallbackQuery):
    data = _ensure_user_data(callback.from_user.id)
    await callback.message.edit_text(MENU_TEXT, reply_markup=reminders_menu_kb(data))
    await callback.answer()


@router.callback_query(F.data == "reminders:toggle_water")
async def cb_toggle_water(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = _ensure_user_data(user_id)
    data["water"]["enabled"] = not data["water"]["enabled"]

    if data["water"]["enabled"]:
        schedule_interval(
            f"water:{user_id}", user_id, WATER_TEXT,
            data["water"]["interval_minutes"], active_hours=(8, 22),
        )
    else:
        unschedule(f"water:{user_id}")

    await callback.message.edit_text(MENU_TEXT, reply_markup=reminders_menu_kb(data))
    await callback.answer()


@router.callback_query(F.data == "reminders:set_vitamins_time")
async def cb_set_vitamins_time(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReminderStates.waiting_for_vitamins_time)
    await callback.message.edit_text(
        "Во сколько удобно получать напоминание про витамины? Напиши время в "
        "формате ЧЧ:ММ, например: 09:00"
    )
    await callback.answer()


@router.message(ReminderStates.waiting_for_vitamins_time)
async def process_vitamins_time(message: Message, state: FSMContext):
    match = TIME_PATTERN.match(message.text.strip())
    if not match:
        await message.answer("Не получилось распознать время 🙈 Напиши в формате ЧЧ:ММ, например: 09:00")
        return

    hour, minute = int(match.group(1)), int(match.group(2))
    user_id = message.from_user.id
    data = _ensure_user_data(user_id)
    data["vitamins"] = {"enabled": True, "time": f"{hour:02d}:{minute:02d}"}

    schedule_daily(f"vitamins:{user_id}", user_id, "💊 Время принять витамины!", hour, minute)

    await state.clear()
    await message.answer(
        f"Готово! Буду напоминать каждый день в {hour:02d}:{minute:02d} 💊",
        reply_markup=reminders_menu_kb(data),
    )


@router.callback_query(F.data == "reminders:toggle_vitamins")
async def cb_toggle_vitamins(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = _ensure_user_data(user_id)
    data["vitamins"]["enabled"] = not data["vitamins"]["enabled"]

    if data["vitamins"]["enabled"] and data["vitamins"]["time"]:
        hour, minute = map(int, data["vitamins"]["time"].split(":"))
        schedule_daily(f"vitamins:{user_id}", user_id, "💊 Время принять витамины!", hour, minute)
    else:
        unschedule(f"vitamins:{user_id}")

    await callback.message.edit_text(MENU_TEXT, reply_markup=reminders_menu_kb(data))
    await callback.answer()


@router.callback_query(F.data == "reminders:add_custom")
async def cb_add_custom(callback: CallbackQuery, state: FSMContext):
    data = _ensure_user_data(callback.from_user.id)
    if len(data["custom"]) >= 5:
        await callback.answer("Уже добавлено максимум (5) — удали что-то, чтобы добавить новое", show_alert=True)
        return

    await state.set_state(ReminderStates.waiting_for_custom_text)
    await callback.message.edit_text("Напиши текст напоминания — то, что я пришлю в нужный момент.")
    await callback.answer()


@router.message(ReminderStates.waiting_for_custom_text)
async def process_custom_text(message: Message, state: FSMContext):
    await state.update_data(custom_text=message.text)

    kb = InlineKeyboardBuilder()
    kb.button(text="Каждый час", callback_data="reminders:custom_interval:60")
    kb.button(text="Каждые 2 часа", callback_data="reminders:custom_interval:120")
    kb.button(text="Каждые 3 часа", callback_data="reminders:custom_interval:180")
    kb.button(text="Каждые 4 часа", callback_data="reminders:custom_interval:240")
    kb.button(text="🕐 Раз в день, в своё время", callback_data="reminders:custom_daily")
    kb.adjust(2, 2, 1)

    await message.answer("Как часто присылать это напоминание?", reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("reminders:custom_interval:"))
async def cb_custom_interval(callback: CallbackQuery, state: FSMContext):
    minutes = int(callback.data.split(":")[2])
    fsm_data = await state.get_data()
    text = fsm_data.get("custom_text", "Напоминание!")

    user_id = callback.from_user.id
    data = _ensure_user_data(user_id)
    reminder_id = uuid.uuid4().hex[:8]
    data["custom"].append({
        "id": reminder_id, "text": text, "type": "interval",
        "interval_minutes": minutes, "time": None, "enabled": True,
    })

    schedule_interval(f"custom:{user_id}:{reminder_id}", user_id, f"🔔 {text}", minutes, active_hours=(8, 22))

    await state.clear()
    await callback.message.edit_text(MENU_TEXT, reply_markup=reminders_menu_kb(data))
    await callback.answer("Добавлено!")


@router.callback_query(F.data == "reminders:custom_daily")
async def cb_custom_daily(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReminderStates.waiting_for_custom_daily_time)
    await callback.message.edit_text("Во сколько присылать это напоминание? Формат ЧЧ:ММ, например: 20:00")
    await callback.answer()


@router.message(ReminderStates.waiting_for_custom_daily_time)
async def process_custom_daily_time(message: Message, state: FSMContext):
    match = TIME_PATTERN.match(message.text.strip())
    if not match:
        await message.answer("Не получилось распознать время 🙈 Напиши в формате ЧЧ:ММ, например: 20:00")
        return

    hour, minute = int(match.group(1)), int(match.group(2))
    fsm_data = await state.get_data()
    text = fsm_data.get("custom_text", "Напоминание!")

    user_id = message.from_user.id
    data = _ensure_user_data(user_id)
    reminder_id = uuid.uuid4().hex[:8]
    data["custom"].append({
        "id": reminder_id, "text": text, "type": "daily",
        "interval_minutes": None, "time": f"{hour:02d}:{minute:02d}", "enabled": True,
    })

    schedule_daily(f"custom:{user_id}:{reminder_id}", user_id, f"🔔 {text}", hour, minute)

    await state.clear()
    await message.answer(
        f"Готово! Буду напоминать каждый день в {hour:02d}:{minute:02d} 🔔",
        reply_markup=reminders_menu_kb(data),
    )


@router.callback_query(F.data.startswith("reminders:toggle_custom:"))
async def cb_toggle_custom(callback: CallbackQuery):
    reminder_id = callback.data.split(":")[2]
    user_id = callback.from_user.id
    data = _ensure_user_data(user_id)

    item = next((i for i in data["custom"] if i["id"] == reminder_id), None)
    if not item:
        await callback.answer()
        return

    item["enabled"] = not item["enabled"]
    job_id = f"custom:{user_id}:{reminder_id}"

    if item["enabled"]:
        if item["type"] == "interval":
            schedule_interval(job_id, user_id, f"🔔 {item['text']}", item["interval_minutes"], active_hours=(8, 22))
        else:
            hour, minute = map(int, item["time"].split(":"))
            schedule_daily(job_id, user_id, f"🔔 {item['text']}", hour, minute)
    else:
        unschedule(job_id)

    await callback.message.edit_text(MENU_TEXT, reply_markup=reminders_menu_kb(data))
    await callback.answer()


@router.callback_query(F.data.startswith("reminders:delete_custom:"))
async def cb_delete_custom(callback: CallbackQuery):
    reminder_id = callback.data.split(":")[2]
    user_id = callback.from_user.id
    data = _ensure_user_data(user_id)

    data["custom"] = [i for i in data["custom"] if i["id"] != reminder_id]
    unschedule(f"custom:{user_id}:{reminder_id}")

    await callback.message.edit_text(MENU_TEXT, reply_markup=reminders_menu_kb(data))
    await callback.answer("Удалено")