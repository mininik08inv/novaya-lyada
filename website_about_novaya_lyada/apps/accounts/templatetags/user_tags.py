from django import template
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount

register = template.Library()

@register.simple_tag
def get_user_avatar(user, size=120):
    """
    Получает аватар пользователя из социальной сети или возвращает дефолтный
    """
    if not user.is_authenticated:
        return ''
    
    # Пытаемся получить аватар из социальной сети
    try:
        social_account = SocialAccount.objects.get(user=user)
        
        if social_account.provider == 'google':
            # Google возвращает аватар в extra_data
            extra_data = social_account.extra_data
            if 'picture' in extra_data:
                return extra_data['picture']
        
        elif social_account.provider == 'vk':
            # VK возвращает аватар в extra_data
            extra_data = social_account.extra_data
            if 'photo' in extra_data:
                return extra_data['photo']
        
    except SocialAccount.DoesNotExist:
        pass
    
    # Если аватар не найден, возвращаем дефолтный
    return '/static/images/default-avatar.png'

@register.simple_tag
def get_user_display_name(user):
    """
    Получает отображаемое имя пользователя из социальной сети или Django
    """
    if not user.is_authenticated:
        return ''
    
    try:
        social_account = SocialAccount.objects.get(user=user)
        
        if social_account.provider == 'google':
            extra_data = social_account.extra_data
            if 'name' in extra_data:
                return extra_data['name']
        
        elif social_account.provider == 'vk':
            extra_data = social_account.extra_data
            if 'first_name' in extra_data and 'last_name' in extra_data:
                return f"{extra_data['first_name']} {extra_data['last_name']}"
            elif 'first_name' in extra_data:
                return extra_data['first_name']
        
    except SocialAccount.DoesNotExist:
        pass
    
    # Возвращаем Django имя или username
    return user.get_full_name() or user.username
