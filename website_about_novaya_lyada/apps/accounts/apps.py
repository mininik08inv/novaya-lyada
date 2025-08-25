from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'website_about_novaya_lyada.apps.accounts'
    verbose_name = 'Аккаунты'

    def ready(self):
        try:
            import accounts.signals
        except ImportError:
            pass


