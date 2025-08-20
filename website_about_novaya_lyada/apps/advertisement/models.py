from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify as dj_slugify
from slugify import slugify as ascii_slugify
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone

User = get_user_model()

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')

class AdvertisementCategory(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=120, unique=True, db_index=True, allow_unicode=True)
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория объявлений"
        verbose_name_plural = "Категории объявлений"

    def __str__(self):
        return self.name


class Advertisement(models.Model):
    STATUS_CHOICES = (
        ("draft", "Черновик"),
        ("published", "Опубликовано"),
        ("archive", "В архиве"),
    )

    title = models.CharField(max_length=200, verbose_name="Заголовок")
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
    content = models.TextField(blank=True, null=True, verbose_name="Текст объявления")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена")
    image = models.ImageField(upload_to="advertisement/%Y/%m/%d/", null=True, blank=True, verbose_name="Изображение")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="ads", verbose_name="Автор")
    category = models.ForeignKey(AdvertisementCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name="ads", verbose_name="Категория")
    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name="Телефон")
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name="Адрес")
    dedline_publish = models.DateTimeField(null=True, blank=True, verbose_name="Дата окончания публикации")

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ("-created",)

    objects = models.Manager()
    published = PublishedManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("advertisement:advertisement_detail", kwargs={"advertisement_slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate ASCII-only slug with transliteration
            base_slug = ascii_slugify(self.title)
            candidate = base_slug
            suffix = 2
            while Advertisement.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = candidate
        self.full_clean()
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            # Логируем ошибку для диагностики
            print(f"Error saving Event: {e}")
            raise

