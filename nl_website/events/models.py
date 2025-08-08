from django.urls import reverse
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.utils.text import slugify

User = get_user_model()


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category", kwargs={"cat_slug": self.slug})


class Event(models.Model):
    STATUS_CHOICES = (
        ("draft", "Черновик"),
        ("published", "Опубликовано"),
        ("archive", "В архиве"),
    )

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    image = models.ImageField(
        upload_to="events/%Y/%m/%d/",
        default=None,
        blank=True,
        null=True,
        verbose_name="Изображение",
    )
    content = models.TextField(blank=True, null=True, verbose_name="Контент")
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="Slug",
        validators=[
            MinLengthValidator(5, message="Минимум 5 символов"),
            MaxLengthValidator(100, message="Максимум 100 символов"),
        ],
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    date_of_event = models.DateTimeField(
        verbose_name="Дата события", default=timezone.now
    )
    created = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated = models.DateTimeField(verbose_name="Дата обновления", auto_now=True)
    author = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events_posts",
        verbose_name="Автор",
        default=None,
    )
    cat = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="events_posts",
        verbose_name="Категории",
    )

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        ordering = ("-date_of_event",)

    objects = models.Manager()
    published = PublishedManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("events:event_detail", kwargs={"event_slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            # Логируем ошибку для диагностики
            print(f"Error saving Event: {e}")
            raise
