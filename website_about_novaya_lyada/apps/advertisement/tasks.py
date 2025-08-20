from celery import shared_task
from django.utils import timezone

from advertisement.models import Advertisement


@shared_task
def expire_advertisements():
    now = timezone.now()
    qs = Advertisement.objects.filter(status='published', dedline_publish__lt=now)
    updated = qs.update(status='archive')
    return updated


