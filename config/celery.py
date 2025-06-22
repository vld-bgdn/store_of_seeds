# store_of_seeds/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

app = Celery("store_of_seeds")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
