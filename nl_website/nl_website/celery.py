import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nl_website.settings')

app = Celery('nl_website')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


