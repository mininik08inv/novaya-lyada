from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount import providers
import os


class Command(BaseCommand):
    help = 'Настройка OAuth приложений для Google и VK'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Пересоздать существующие приложения',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('🔧 Настройка OAuth приложений...'))
        
        # Получаем или создаем сайт
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={'domain': 'novaya-lyada.ru', 'name': 'Novaya Lyada'}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Создан сайт: {site.domain}'))
        
        # Настройка Google OAuth
        self.setup_google_oauth(site, force)
        
        # Настройка VK OAuth
        self.setup_vk_oauth(site, force)
        
        self.stdout.write(self.style.SUCCESS('\n✅ Настройка OAuth завершена!'))
        self.stdout.write(self.style.WARNING('\n⚠️  Не забудьте:'))
        self.stdout.write('1. Добавить переменные GOOGLE_CLIENT_ID и GOOGLE_CLIENT_SECRET в .env')
        self.stdout.write('2. Добавить переменные VK_CLIENT_ID и VK_CLIENT_SECRET в .env')
        self.stdout.write('3. Настроить Redirect URIs в Google Console и VK Dev')

    def setup_google_oauth(self, site, force):
        """Настройка Google OAuth"""
        google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if not google_client_id or not google_client_secret:
            self.stdout.write(
                self.style.WARNING('⚠️  Google OAuth: CLIENT_ID или CLIENT_SECRET не найдены в переменных среды')
            )
            return
        
        # Проверяем существование приложения
        existing_app = SocialApp.objects.filter(provider='google').first()
        
        if existing_app and not force:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Google OAuth приложение уже существует (ID: {existing_app.id})')
            )
            self.stdout.write('   Используйте --force для пересоздания')
            return
        
        if existing_app and force:
            existing_app.delete()
            self.stdout.write(self.style.SUCCESS('🗑️  Старое Google OAuth приложение удалено'))
        
        # Создаем новое приложение
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth',
            client_id=google_client_id,
            secret=google_client_secret,
        )
        
        google_app.sites.add(site)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Google OAuth настроен (ID: {google_app.id})'))
        self.stdout.write(f'   Client ID: {google_client_id[:20]}...')

    def setup_vk_oauth(self, site, force):
        """Настройка VK OAuth"""
        vk_client_id = os.getenv('VK_CLIENT_ID')
        vk_client_secret = os.getenv('VK_CLIENT_SECRET')
        
        if not vk_client_id or not vk_client_secret:
            self.stdout.write(
                self.style.WARNING('⚠️  VK OAuth: CLIENT_ID или CLIENT_SECRET не найдены в переменных среды')
            )
            return
        
        # Проверяем существование приложения
        existing_app = SocialApp.objects.filter(provider='vk').first()
        
        if existing_app and not force:
            self.stdout.write(
                self.style.WARNING(f'⚠️  VK OAuth приложение уже существует (ID: {existing_app.id})')
            )
            self.stdout.write('   Используйте --force для пересоздания')
            return
        
        if existing_app and force:
            existing_app.delete()
            self.stdout.write(self.style.SUCCESS('🗑️  Старое VK OAuth приложение удалено'))
        
        # Создаем новое приложение
        vk_app = SocialApp.objects.create(
            provider='vk',
            name='VK OAuth',
            client_id=vk_client_id,
            secret=vk_client_secret,
        )
        
        vk_app.sites.add(site)
        
        self.stdout.write(self.style.SUCCESS(f'✅ VK OAuth настроен (ID: {vk_app.id})'))
        self.stdout.write(f'   Client ID: {vk_client_id}')
