import os
import asyncpg
from handlers import storage

_pool = None


async def init_db():
    """Подключается к базе, создаёт таблицу (если её ещё нет) и загружает сохранённые данные."""
    global _pool
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("⚠️ DATABASE_URL не найден в .env — данные НЕ будут сохраняться между перезапусками!")
        return

    try:
        _pool = await asyncpg.create_pool(database_url, min_size=1, max_size=3)

        async with _pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS bot_state (
                    id INTEGER PRIMARY KEY,
                    data TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT now()
                )
                """
            )

        await load_state()
        print("✅ Подключение к базе данных установлено.")
    except Exception as e:
        print(f"❌ Не удалось подключиться к базе данных: {e}")
        _pool = None


async def load_state():
    if _pool is None:
        return
    async with _pool.acquire() as conn:
        row = await conn.fetchrow("SELECT data FROM bot_state WHERE id = 1")
        if row:
            storage.import_state(row["data"])
            print("✅ Данные загружены из базы.")
        else:
            print("ℹ️ В базе пока нет сохранённых данных — начинаем с чистого листа.")


async def save_state():
    if _pool is None:
        return
    try:
        raw = storage.export_state()
        async with _pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO bot_state (id, data, updated_at)
                VALUES (1, $1, now())
                ON CONFLICT (id) DO UPDATE SET data = $1, updated_at = now()
                """,
                raw,
            )
    except Exception as e:
        print(f"❌ Ошибка при сохранении в базу: {e}")


async def close_db():
    if _pool is not None:
        await save_state()
        await _pool.close()
        print("💾 Данные сохранены перед остановкой.")