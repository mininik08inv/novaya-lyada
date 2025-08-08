# tests/test_models.py
import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from unittest.mock import patch, MagicMock
from events.models import Event, User  # Замените на реальный путь к модели

@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpass")

@patch('your_app.models.Event.image.field.upload_to', return_value='events/2023/01/01/')  # Замените на реальный путь
def test_event_slug_generation(mock_upload_to, db, user):
    """Тест генерации slug при отсутствии значения."""
    event = Event.objects.create(
        title="Тестовое событие",
        author=user
    )
    assert event.slug == slugify("Тестовое событие")

@patch('your_app.models.Event.image.field.upload_to', return_value='events/2023/01/01/')
def test_event_slug_not_overwritten(mock_upload_to, db, user):
    """Тест: slug не перезаписывается, если уже задан."""
    event = Event.objects.create(
        title="Тестовое событие",
        slug="custom-slug",
        author=user
    )
    assert event.slug == "custom-slug"

@patch('your_app.models.Event.image.field.upload_to', return_value='events/2023/01/01/')
def test_event_slug_length_validation(mock_upload_to, db, user):
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

@patch('your_app.models.Event.image.field.upload_to', return_value='events/2023/01/01/')
def test_event_status_default(mock_upload_to, db, user):
    """Тест значения по умолчанию для status."""
    event = Event.objects.create(title="Событие", author=user)
    assert event.status == "draft"

@patch('your_app.models.Event.image.field.upload_to', return_value='events/2023/01/01/')
def test_event_updated_timestamp(mock_upload_to, db, user):
    """Тест автоматического обновления поля `updated`."""
    event = Event.objects.create(title="Событие", author=user)
    initial_update_time = event.updated
    event.save()
    assert event.updated > initial_update_time

@patch('your_app.models.Event.image.field.upload_to', return_value='events/2023/01/01/')
def test_event_get_absolute_url(mock_upload_to, db, user):
    """Тест метода `get_absolute_url`."""
    event = Event.objects.create(title="Событие", slug="event-slug", author=user)
    assert event.get_absolute_url() == reverse('events:event_detail', kwargs={'event_slug': 'event-slug'})

@patch('your_app.models.Event.image.field.upload_to', return_value='events/2023/01/01/')
def test_event_str_representation(mock_upload_to, db, user):
    """Тест метода `__str__`."""
    event = Event.objects.create(title="Событие", author=user)
    assert str(event) == "Событие"

@patch('your_app.models.Event.image.field.upload_to', return_value='events/2023/01/01/')
def test_event_without_image(mock_upload_to, db, user):
    """Тест создания события без изображения."""
    event = Event.objects.create(title="Событие", author=user)
    assert event.image is None

@patch('your_app.models.Event.image.field.upload_to', return_value='events/2023/01/01/')
def test_event_ordering(mock_upload_to, db, user):
    """Тест сортировки по `-date_of_event`."""
    event1 = Event.objects.create(title="Событие 1", author=user, date_of_event=timezone.now())
    event2 = Event.objects.create(title="Событие 2", author=user, date_of_event=timezone.now() + timezone.timedelta(days=1))
    events = Event.objects.all()
    assert list(events) == [event2, event1]
