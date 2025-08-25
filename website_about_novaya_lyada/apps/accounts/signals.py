from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount


@receiver(post_save, sender=SocialAccount)
def update_user_profile_from_social(sender, instance, created, **kwargs):
    """
    Автоматически обновляет профиль пользователя данными из социальной сети
    """
    if created and instance.user:
        user = instance.user
        extra_data = instance.extra_data
        
        # Обновляем имя пользователя из соцсети
        if instance.provider == 'google':
            if 'name' in extra_data and not user.first_name:
                user.first_name = extra_data['name']
            if 'given_name' in extra_data and not user.first_name:
                user.first_name = extra_data['given_name']
            if 'family_name' in extra_data and not user.last_name:
                user.last_name = extra_data['family_name']
        
        elif instance.provider == 'vk':
            if 'first_name' in extra_data and not user.first_name:
                user.first_name = extra_data['first_name']
            if 'last_name' in extra_data and not user.last_name:
                user.last_name = extra_data['last_name']
        
        # Сохраняем изменения
        if user.first_name or user.last_name:
            user.save()
