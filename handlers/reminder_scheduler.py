from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()
_bot = None


def set_bot(bot):
    """Передаём боту доступ к экземпляру Bot, чтобы можно было отправлять сообщения из фона."""
    global _bot
    _bot = bot


def start_scheduler():
    if not scheduler.running:
        scheduler.start()


async def _send_reminder(user_id: int, text: str, active_hours=None):
    if _bot is None:
        return

    if active_hours:
        start_h, end_h = active_hours
        now_h = datetime.now().hour
        if not (start_h <= now_h < end_h):
            return  # не беспокоим ночью

    try:
        await _bot.send_message(user_id, text)
    except Exception as e:
        print(f"Не удалось отправить напоминание пользователю {user_id}: {e}")


def schedule_interval(job_id: str, user_id: int, text: str, minutes: int, active_hours=None):
    scheduler.add_job(
        _send_reminder,
        trigger=IntervalTrigger(minutes=minutes),
        args=[user_id, text, active_hours],
        id=job_id,
        replace_existing=True,
        next_run_time=datetime.now() + timedelta(minutes=minutes),
    )


def schedule_daily(job_id: str, user_id: int, text: str, hour: int, minute: int):
    scheduler.add_job(
        _send_reminder,
        trigger=CronTrigger(hour=hour, minute=minute),
        args=[user_id, text, None],
        id=job_id,
        replace_existing=True,
    )


def unschedule(job_id: str):
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass