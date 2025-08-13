from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.urls import reverse

User = get_user_model()


class CategoryPlace(models.Model):
    """Модель категории мест"""
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL категории")
    description = models.TextField(blank=True, null=True, verbose_name="Описание категории")

    class Meta:
        verbose_name = "Категория мест"
        verbose_name_plural = "Категории мест"

    def __str__(self):
        return self.name

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class Place(models.Model):
    """Модель места"""
    name = models.CharField(max_length=200, verbose_name="Название места")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL категории")
    description = models.TextField(verbose_name="Описание места")
    address = models.CharField(max_length=300, verbose_name="Адрес")
    latitude = models.FloatField(null=True, blank=True, verbose_name="Широта")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Долгота")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")
    categories = models.ManyToManyField(CategoryPlace, related_name="places", verbose_name="Категории")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Автор")

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


    def get_average_rating(self):
        """Возвращает средний рейтинг места на основе отзывов"""
        # Используем агрегацию для вычисления среднего значения
        result = self.reviews.aggregate(average_rating=Avg('rating'))

        # Если нет отзывов, возвращаем 0
        return result['average_rating'] or 0

    def get_rating_percentage(self):
        """Возвращает рейтинг в процентах (для использования в шаблонах)"""
        return (self.get_average_rating() / 5) * 100

    objects = models.Manager()
    published = PublishedManager()


class PlacePhoto(models.Model):
    """Модель фотографии места"""
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="photos", verbose_name="Место")
    photo = models.ImageField(upload_to="places/photos/", verbose_name="Фотография")
    is_main = models.BooleanField(default=False, verbose_name="Главная фотография")

    class Meta:
        verbose_name = "Фотография места"
        verbose_name_plural = "Фотографии мест"
        ordering = ['-is_main', 'id']

    def __str__(self):
        return f"Фото для {self.place.name}"


class PlaceReview(models.Model):
    """Модель отзыва о месте"""
    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Удовлетворительно'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]

    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="reviews", verbose_name="Место")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор отзыва")
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Рейтинг")
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Отзыв о месте"
        verbose_name_plural = "Отзывы о местах"
        ordering = ['-created_at']
        unique_together = ['place', 'author']  # Один пользователь - один отзыв на место

    def __str__(self):
        return f"Отзыв от {self.author} на {self.place.name}"