from celery import Celery
from app.config import get_settings, Settings

settings: Settings = get_settings()

app = Celery(__name__)
app.conf.broker_url = settings.REDIS_URL
app.conf.result_backend = settings.REDIS_URL
