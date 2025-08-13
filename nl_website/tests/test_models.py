# tests/test_models.py
import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from events.models import Event
from django.contrib.auth import get_user_model

@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username="testuser", password="testpass")

from events.models import Category


@pytest.fixture
def category(db):
    return Category.objects.create(name="Новости", slug="novosti")


def test_event_slug_generation(db, user, category):
    """Тест генерации slug при отсутствии значения."""
    event = Event.objects.create(
        title="Тестовое событие",
        author=user,
        cat=category
    )
    assert event.slug == slugify("Тестовое событие", allow_unicode=True)

def test_event_slug_not_overwritten(db, user, category):
    """Тест: slug не перезаписывается, если уже задан."""
    event = Event.objects.create(
        title="Тестовое событие",
        slug="custom-slug",
        author=user,
        cat=category
    )
    assert event.slug == "custom-slug"

def test_event_slug_length_validation(db, user):
    """Тест валидации длины slug."""
    with pytest.raises(ValidationError) as exc_info:
        Event.objects.create(
            title="Тест",
            slug="a" * 4,  # <5 символов
            author=user
        )
    assert "Минимум 5 символов" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        Event.objects.create(
            title="Тест",
            slug="a" * 101,  # >100 символов
            author=user
        )
    assert "Максимум 100 символов" in str(exc_info.value)

def test_event_status_default(db, user, category):
    """Тест значения по умолчанию для status."""
    event = Event.objects.create(title="Событие", author=user, cat=category)
    assert event.status == "draft"

def test_event_updated_timestamp(db, user, category):
    """Тест автоматического обновления поля `updated`."""
    event = Event.objects.create(title="Событие", author=user, cat=category)
    initial_update_time = event.updated
    event.save()
    assert event.updated > initial_update_time

def test_event_get_absolute_url(db, user, category):
    """Тест метода `get_absolute_url`."""
    event = Event.objects.create(title="Событие", slug="event-slug", author=user, cat=category)
    assert event.get_absolute_url() == reverse('events:event_detail', kwargs={'event_slug': 'event-slug'})

def test_event_str_representation(db, user, category):
    """Тест метода `__str__`."""
    event = Event.objects.create(title="Событие", author=user, cat=category)
    assert str(event) == "Событие"

def test_event_without_image(db, user, category):
    """Тест создания события без изображения."""
    event = Event.objects.create(title="Событие", author=user, cat=category)
    assert not event.image

def test_event_ordering(db, user, category):
    """Тест сортировки по `-date_of_event`."""
    event1 = Event.objects.create(title="Событие 1", author=user, cat=category, date_of_event=timezone.now())
    event2 = Event.objects.create(title="Событие 2", author=user, cat=category, date_of_event=timezone.now() + timezone.timedelta(days=1))
    events = Event.objects.all()
    assert list(events) == [event2, event1]
