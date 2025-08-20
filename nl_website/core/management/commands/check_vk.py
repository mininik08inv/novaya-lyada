from django.core.management.base import BaseCommand
from django.conf import settings
from allauth.socialaccount.models import SocialApp
import os


class Command(BaseCommand):
    help = 'Проверка настроек VK OAuth'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔵 Проверка VK OAuth настроек...\n'))
        
        # Проверяем переменные среды
        vk_client_id = os.getenv('VK_CLIENT_ID')
        vk_client_secret = os.getenv('VK_CLIENT_SECRET')
        
        self.stdout.write('📋 Переменные среды:')
        if vk_client_id and vk_client_id != 'your_vk_app_id_here':
            self.stdout.write(f'   ✅ VK_CLIENT_ID: {vk_client_id}')
        else:
            self.stdout.write('   ❌ VK_CLIENT_ID: не установлен или содержит заглушку')
        
        if vk_client_secret and vk_client_secret != 'your_vk_secret_here':
            self.stdout.write(f'   ✅ VK_CLIENT_SECRET: {"*" * len(vk_client_secret)}')
        else:
            self.stdout.write('   ❌ VK_CLIENT_SECRET: не установлен или содержит заглушку')
        
        # Проверяем настройки Django
        self.stdout.write('\n⚙️ Настройки Django:')
        vk_config = settings.SOCIALACCOUNT_PROVIDERS.get('vk', {})
        if vk_config:
            self.stdout.write('   ✅ VK провайдер настроен в SOCIALACCOUNT_PROVIDERS')
            
            app_config = vk_config.get('APP', {})
            client_id = app_config.get('client_id', '')
            secret = app_config.get('secret', '')
            
            if client_id:
                self.stdout.write(f'   ✅ Client ID в настройках: {client_id}')
            else:
                self.stdout.write('   ❌ Client ID не найден в настройках')
                
            if secret:
                self.stdout.write(f'   ✅ Secret в настройках: {"*" * len(secret)}')
            else:
                self.stdout.write('   ❌ Secret не найден в настройках')
        else:
            self.stdout.write('   ❌ VK провайдер не найден в SOCIALACCOUNT_PROVIDERS')
        
        # Проверяем SocialApp в базе данных
        self.stdout.write('\n🗄️ Приложения в базе данных:')
        vk_apps = SocialApp.objects.filter(provider='vk')
        
        if vk_apps.exists():
            for app in vk_apps:
                self.stdout.write(f'   ✅ VK приложение найдено:')
                self.stdout.write(f'      ID: {app.id}')
                self.stdout.write(f'      Name: {app.name}')
                self.stdout.write(f'      Client ID: {app.client_id}')
                self.stdout.write(f'      Secret: {"установлен" if app.secret else "НЕ установлен"}')
                
                sites = list(app.sites.values_list('domain', flat=True))
                self.stdout.write(f'      Сайты: {sites if sites else "не привязаны"}')
        else:
            self.stdout.write('   ❌ VK приложения не найдены в базе данных')
        
        # Проверяем URL маршруты
        self.stdout.write('\n🔗 URL маршруты:')
        try:
            from django.urls import reverse
            vk_login_url = reverse('socialaccount_login', kwargs={'provider': 'vk'})
            self.stdout.write(f'   ✅ VK login URL: {vk_login_url}')
            
            expected_callback = '/accounts/vk/login/callback/'
            self.stdout.write(f'   ℹ️  Expected callback: {expected_callback}')
        except Exception as e:
            self.stdout.write(f'   ❌ Ошибка URL: {e}')
        
        # Рекомендации
        self.stdout.write(self.style.WARNING('\n💡 Рекомендации:'))
        
        if not vk_client_id or vk_client_id == 'your_vk_app_id_here':
            self.stdout.write('   1. Создайте VK приложение на https://dev.vk.com/')
            self.stdout.write('   2. Добавьте VK_CLIENT_ID в .env файл')
        
        if not vk_client_secret or vk_client_secret == 'your_vk_secret_here':
            self.stdout.write('   3. Добавьте VK_CLIENT_SECRET в .env файл')
        
        if not vk_apps.exists() and vk_client_id and vk_client_secret:
            self.stdout.write('   4. Выполните: python manage.py setup_oauth')
        
        self.stdout.write('\n🌐 Redirect URIs для VK приложения:')
        self.stdout.write('   • http://127.0.0.1:8000/accounts/vk/login/callback/')
        self.stdout.write('   • http://localhost:8000/accounts/vk/login/callback/')
        self.stdout.write('   • https://novaya-lyada.ru/accounts/vk/login/callback/')
        
        self.stdout.write('\n✅ Проверка завершена!')
