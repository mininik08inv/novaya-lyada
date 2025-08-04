from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    # Базовые поля (уже есть в AbstractUser):
    # username, email, first_name, last_name, password, etc.

    # Telegram данные
    telegram_id = models.BigIntegerField(
        _('Telegram ID'),
        unique=True,
        null=True,
        blank=True,
        help_text=_('Уникальный идентификатор пользователя в Telegram')
    )
    telegram_username = models.CharField(
        _('Telegram username'),
        max_length=32,
        null=True,
        blank=True,
        help_text=_('Username в Telegram (без @)')
    )
    telegram_photo = models.URLField(
        _('Telegram Photo'),
        null=True,
        blank=True,
        help_text=_('Ссылка на аватарку из Telegram')
    )

    # VK данные
    vk_id = models.BigIntegerField(
        _('VK ID'),
        unique=True,
        null=True,
        blank=True,
        help_text=_('Уникальный идентификатор пользователя во ВКонтакте')
    )
    vk_username = models.CharField(
        _('VK Username'),
        max_length=50,
        null=True,
        blank=True,
        help_text=_('Короткое имя (domain) пользователя в VK')
    )
    vk_photo = models.URLField(
        _('VK Photo'),
        null=True,
        blank=True,
        help_text=_('Ссылка на аватарку из VK')
    )

    # Общие поля
    registration_method = models.CharField(
        _('Registration Method'),
        max_length=10,
        choices=[
            ('email', 'Email'),
            ('telegram', 'Telegram'),
            ('vk', 'VKontakte'),
        ],
        default='email'
    )
    avatar = models.URLField(
        _('Avatar URL'),
        null=True,
        blank=True,
        help_text=_('Основная аватарка пользователя')
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

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