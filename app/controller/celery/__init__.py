from celery.schedules import crontab
from .app import app
from app.config import get_settings, Settings
from app.logger import log

settings: Settings = get_settings()


@app.task
def pay_plus_fee():
    from app.controller.platform_payment import collect_fee

    return collect_fee()


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    log(log.INFO, "Configure scheduler")

    log(
        log.INFO,
        "Run weekly collecting fee on %02d:%02d",
        settings.DAILY_REPORT_HOURS,
        settings.DAILY_REPORT_MINUTES,
    )
    sender.add_periodic_task(
        crontab(
            day_of_week=settings.FEE_PAY_DAY,
            hour=settings.DAILY_REPORT_HOURS,
            minute=settings.DAILY_REPORT_MINUTES,
        ),
        pay_plus_fee.s(),
        name="Weekly collecting fee",
    )
    log(log.INFO, "Tasks scheduled!")
