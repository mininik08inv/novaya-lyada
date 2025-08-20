from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth import get_user_model

User = get_user_model()

def transliterate_russian(text):
    """Простая транслитерация русского текста в латиницу"""
    trans_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    
    result = ''
    for char in text:
        result += trans_map.get(char, char)
    return result

# Create your models here.
class ImprovementIdea(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('collection', 'Сбор голосов'),
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрен'),
        ('rejected', 'Отклонен'),
        ('implemented', 'Реализован'),
    ]

    CATEGORY_CHOICES = [
        ('transport', 'Транспорт'),
        ('infrastructure', 'Инфраструктура'),
        ('tourism', 'Туризм'),
        ('culture', 'Культура'),
        ('education', 'Образование'),
        ('health', 'Здоровье'),
        ('environment', 'Экология'),
        ('culture', 'Культура'),
        ('security', 'Безопасность'),
        ('leisure', 'Досуг'),
        ('other', 'Другое'),
        
    ]
    title = models.CharField(max_length=255, verbose_name='Название')
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name='Slug',
        validators=[
            MinLengthValidator(5, message="Минимум 5 символов"),
            MaxLengthValidator(100, message="Максимум 100 символов"),
        ],
    )
    description = models.TextField(verbose_name='Описание')
    proposed_solution = models.TextField(verbose_name='Предлагаемое решение')
    location = models.CharField(max_length=255, verbose_name='Местоположение')
    image = models.ImageField(upload_to='idea_images/', null=True, blank=True, verbose_name='Изображение')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Категория')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = "Идея улучшения"
        verbose_name_plural = "Идеи улучшений"
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("ideas:idea_detail", kwargs={"idea_slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            # Транслитерируем русский текст в латиницу
            transliterated = transliterate_russian(self.title)
            
            # Генерируем slug на английском
            base_slug = slugify(transliterated)
            candidate = base_slug
            suffix = 2
            
            # Проверяем уникальность slug
            while ImprovementIdea.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{suffix}"
                suffix += 1
            
            self.slug = candidate
        
        # Проверяем валидность перед сохранением
        self.full_clean()
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            # Логируем ошибку для диагностики
            print(f"Error saving ImprovementIdea: {e}")
            raise

class IdeaComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    idea = models.ForeignKey(ImprovementIdea, on_delete=models.CASCADE, verbose_name='Идея')
    text = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

class IdeaVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    idea = models.ForeignKey(ImprovementIdea, on_delete=models.CASCADE, verbose_name='Идея')
    vote_type = models.CharField(max_length=10, choices=[('up', 'Голос за'), ('down', 'Голос против')], verbose_name='Тип голоса')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')