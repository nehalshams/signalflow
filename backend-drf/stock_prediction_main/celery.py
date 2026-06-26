"""Celery application for stock_prediction_main.

Started via:
    celery -A stock_prediction_main worker -l info          # worker
    celery -A stock_prediction_main beat   -l info          # scheduler
"""
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_prediction_main.settings')

app = Celery('stock_prediction_main')

# Pull every CELERY_* setting from Django settings.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks.py modules in all installed apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
