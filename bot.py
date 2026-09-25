import json
import random
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

with open("faq.json", "r", encoding="utf-8") as f:
    knowledge_base = json.load(f)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DISCLAIMER = "⚠️ Этот бот не заменяет консультацию врача. Все вопросы о здоровье обсуждай с врачом."

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    logging.info(f"Получен /start от {message.from_user.id}")
    await message.answer(
        f"Привет, дорогая! 🤗\n{DISCLAIMER}\n\n"
        "Я рядом — отвечу на вопросы, пришлю доброе слово. "
        "Просто напиши, что волнует, или скажи «хочу поддержки»."
    )

@dp.message()
async def handle_message(message: types.Message):
    text = message.text.lower()
    logging.info(f"Сообщение от {message.from_user.id}: {message.text}")

    for item in knowledge_base["faq"]:
        words = item["question"].lower().split()
        if any(word in text for word in words if len(word) > 3):
            await message.answer(item["answer"])
            return

    if any(k in text for k in ["устала", "страшно", "тяжело", "поддержки", "обними", "хочу поддержки"]):
        aff = random.choice(knowledge_base["affirmations"])
        await message.answer(f"🤗 {aff}")
        return

    await message.answer("Пока не нашла точного ответа. Напиши подробнее — или скажи «хочу поддержки».")

async def on_startup(bot: Bot):
    webhook_path = f"/{BOT_TOKEN}"
    full_url = f"{WEBHOOK_URL}{webhook_path}"
    await bot.set_webhook(url=full_url)
    logging.info(f"Webhook установлен: {full_url}")

dp.startup.register(on_startup)

def main():
    app = web.Application()
    webhook_path = f"/{BOT_TOKEN}"
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=webhook_path)
    setup_application(app, dp, bot=bot)
    port = int(os.getenv("PORT", 8080))
    logging.info(f"Запуск на порту {port}...")
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
