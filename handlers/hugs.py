import random
from aiogram import Router, F
from aiogram.types import CallbackQuery

from handlers.keyboards import back_to_main_kb

router = Router()

HUG_PHRASES = [
    "🤗 Обнимаю тебя крепко-крепко. Ты большая молодец.",
    "🤗 Просто напоминаю: ты справляешься лучше, чем думаешь.",
    "🤗 Если сейчас тяжело — это нормально. Я рядом.",
    "🤗 Ты делаешь невероятную работу каждый день, даже когда это незаметно.",
    "🤗 Пусть эти объятия почувствуются, даже если они всего лишь текст на экране.",
    "🤗 Вдохни поглубже. Всё идёт своим чередом, и ты не одна.",
    "🤗 Малыш чувствует твою заботу каждую секунду. Ты уже прекрасная мама.",
    "🤗 Немного тепла для тебя прямо сейчас — просто так, без повода.",
    "🤗 Ты имеешь право устать. И имеешь право на этот маленький перерыв.",
    "🤗 Каждый день приближает тебя к встрече с малышом. Ты справишься.",
]


@router.callback_query(F.data == "hug:get")
async def cb_hug_get(callback: CallbackQuery):
    phrase = random.choice(HUG_PHRASES)
    await callback.message.edit_text(phrase, reply_markup=back_to_main_kb())
    await callback.answer("🤗")