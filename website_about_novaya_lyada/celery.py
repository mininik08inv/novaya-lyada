import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website_about_novaya_lyada.settings.production')

app = Celery('nl_website')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


