from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Базовые поля (уже есть в AbstractUser):
    # username, email, first_name, last_name, password, etc.

    # Telegram данные
    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
        help_text="Уникальный идентификатор пользователя в Telegram",
    )
    telegram_username = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text="Username в Telegram (без @)",
    )
    telegram_photo = models.URLField(
        null=True,
        blank=True,
        help_text="Ссылка на аватарку из Telegram",
    )

    # VK данные
    vk_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
        help_text="Уникальный идентификатор пользователя во ВКонтакте",
    )
    vk_username = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Короткое имя (domain) пользователя в VK",
    )
    vk_photo = models.URLField(
        null=True, blank=True, help_text="Ссылка на аватарку из VK"
    )

    # Общие поля
    registration_method = models.CharField(
        max_length=10,
        choices=[
            ("email", "Email"),
            ("telegram", "Telegram"),
            ("vk", "VKontakte"),
        ],
        default="email",
    )
    avatar = models.URLField(
        null=True,
        blank=True,
        help_text="Основная аватарка пользователя",
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_display_name()

    def get_display_name(self):
        """Возвращает удобочитаемое имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.telegram_username:
            return f"@{self.telegram_username}"
        if self.vk_username:
            return self.vk_username
        return self.username

    def set_avatar(self):
        """Автоматически выбирает аватар из доступных источников"""
        if self.telegram_photo:
            self.avatar = self.telegram_photo
        if self.vk_photo:
            self.avatar = self.vk_photo
        # Можно добавить загрузку аватарки по умолчанию
