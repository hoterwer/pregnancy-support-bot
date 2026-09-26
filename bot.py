import os
import asyncio
from aiogram import Bot, Dispatcher
from handlers.basic import router as basic_router

async def main():
    # Получаем токен из переменных окружения (Render или .env)
    token = "8861512795:AAHpj6puYi-BKM1gunyKPacRwlBI04Ccc48"
    if not token:
        print("ОШИБКА: Не найден BOT_TOKEN в переменных окружения!")
        return
        
    bot = Bot(token=token)
    dp = Dispatcher()
    
    # Подключаем наш роутер с кнопками и поиском
    dp.include_router(basic_router)
    
    # Запуск поллинга (опрос сервера Telegram)
    # Если у тебя на Render настроен вебхук, этот блок можно заменить на запуск вебхука,
    # но для тестов и простоты оставим polling.
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
