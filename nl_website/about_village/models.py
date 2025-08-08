from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


USER = get_user_model()

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)



class CategoryPeople(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        verbose_name = "Категория людей"
        verbose_name_plural = "Категории известных людей"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category", kwargs={"cat_slug": self.slug})


class FamousPerson(models.Model):
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
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    patronymic = models.CharField(max_length=50, verbose_name="Отчество")
    photo = models.ImageField(
        upload_to="famous_people/%Y/%m/%d/",
        default=None,
        blank=True,
        null=True,
        verbose_name="Фото",
    )
    biography = models.TextField(blank=True, null=True, verbose_name="Биография")
    interesting_facts = models.TextField(blank=True, null=True, verbose_name="Интересные факты")
    categories = models.ManyToManyField(CategoryPeople, verbose_name="Категории")
    place_of_birth = models.CharField(blank=True, null=True, verbose_name="Место рождения")
    date_of_birth = models.DateField(verbose_name="Дата рождения")
    date_of_death = models.DateField(
        null=True, blank=True, verbose_name="Дата смети"
    )
    is_published = models.BooleanField(default=True)
    created = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated = models.DateTimeField(verbose_name="Дата обновления", auto_now=True)
    author = models.ForeignKey(USER, on_delete=models.SET_NULL, null=True,)

    class Meta:
        verbose_name = "Известный человек"
        verbose_name_plural = "Известные люди"

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    def get_absolute_url(self):
        return reverse("about_village:person_detail", kwargs={"person_slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.last_name}-{self.first_name}-{self.patronymic}')
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            # Логируем ошибку для диагностики
            print(f"Error saving Famous people: {e}")
            raise

    objects = models.Manager()
    published = PublishedManager()