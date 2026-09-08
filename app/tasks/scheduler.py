from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import asyncio

from app.database import session_local
from app.crud.subscription import deactivate_expired_subscriptions, get_subscriptions_expiring_soon
from app.utils.email import send_expiration_reminder_email


scheduler = AsyncIOScheduler()

logger = logging.getLogger(__name__)


async def deactive_expire_subscriptions_task():
    async with session_local() as session:
        count = await deactivate_expired_subscriptions(session)
        if count > 0:
            logger.info(f"Deactivated {count} expired subscriptions")
        else:
            logger.debug("No expired subscriptions found")


async def send_expiration_reminders_task():
    async with session_local() as session:
        subs = await get_subscriptions_expiring_soon(session)
        if len(subs) > 0:
            logger.info(f"Sending reminders for {len(subs)} subscriptions")
        else:
            logger.debug("No subscriptions expiring in 3 days")
        for sub in subs:
            send_expiration_reminder_email(sub.student.email, sub.course.title, sub.end_date)


def start_scheduler():

    scheduler.add_job(
        func=deactive_expire_subscriptions_task,
        trigger=CronTrigger(hour=0, minute=0),
        id = "deactivate_subscriptions_cron",
        replace_existing=True,
        max_instances=(1)
    )
    scheduler.add_job(
        func=send_expiration_reminders_task,
        trigger=CronTrigger(hour=9, minute=0),
        id = "send_expiration_email_cron",
        replace_existing=True,
        max_instances=1
    )
    scheduler.start()
    logger.info("Scheduler started successfully")
    return scheduler


def stop_scheduler(scheduler):

    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")