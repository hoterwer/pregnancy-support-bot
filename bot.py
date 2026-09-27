import os
import asyncio
from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from apscheduler.triggers.interval import IntervalTrigger

from handlers.basic import router as basic_router
from handlers.tracker import router as tracker_router
from handlers.kicks import router as kicks_router
from handlers.ai_chat import router as ai_chat_router
from handlers.mood import router as mood_router
from handlers.checklist import router as checklist_router
from handlers.contractions import router as contractions_router
from handlers.letters import router as letters_router
from handlers.hugs import router as hugs_router
from handlers.partner_tips import router as partner_tips_router
from handlers.reading import router as reading_router
from handlers.doctor_questions import router as doctor_questions_router
from handlers.prep_checklist import router as prep_checklist_router
from handlers.symptoms import router as symptoms_router
from handlers.self_care import router as self_care_router
from handlers.daily_joy import router as daily_joy_router
from handlers.reminders import router as reminders_router
from handlers.reminder_scheduler import set_bot, start_scheduler, scheduler

import db

load_dotenv()


async def start_web_server():
    """Крошечный веб-сервер, чтобы Render считал сервис 'живым' веб-сервисом.
    Также сюда стучится внешний сервис, чтобы бот не засыпал (настроим позже)."""
    app = web.Application()
    app.router.add_get("/", lambda request: web.Response(text="Бот работает 💛"))

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"🌐 Веб-сервер запущен на порту {port}")


async def main():
    token = os.getenv("BOT_TOKEN")

    if not token or token.startswith("123"):
        print("❌ ОШИБКА: Проверь, что в файле .env указан реальный токен!")
        return

    bot = Bot(token=token)
    dp = Dispatcher()

    await db.init_db()

    set_bot(bot)
    start_scheduler()
    scheduler.add_job(db.save_state, IntervalTrigger(minutes=2), id="autosave", replace_existing=True)

    dp.include_router(tracker_router)
    dp.include_router(kicks_router)
    dp.include_router(ai_chat_router)
    dp.include_router(mood_router)
    dp.include_router(checklist_router)
    dp.include_router(contractions_router)
    dp.include_router(letters_router)
    dp.include_router(hugs_router)
    dp.include_router(partner_tips_router)
    dp.include_router(reading_router)
    dp.include_router(doctor_questions_router)
    dp.include_router(prep_checklist_router)
    dp.include_router(symptoms_router)
    dp.include_router(self_care_router)
    dp.include_router(daily_joy_router)
    dp.include_router(reminders_router)
    dp.include_router(basic_router)

    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Вебхук удалён — конфликт устранён.")
    print("🚀 Бот запущен и ждёт сообщения в Телеграме! Напиши /start.")

    try:
        # Запускаем одновременно и бота, и веб-сервер
        await asyncio.gather(
            dp.start_polling(bot),
            start_web_server(),
        )
    finally:
        await db.close_db()


if __name__ == "__main__":
    asyncio.run(main())