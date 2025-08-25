from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from website_about_novaya_lyada.apps.advertisement.models import Advertisement
from django.conf import settings
from allauth.socialaccount.models import SocialAccount


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'account/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['default_image'] = getattr(settings, 'DEFAULT_USER_IMAGE', '')
        context['my_ads'] = Advertisement.objects.filter(author=user).order_by('-created')
        
        # Добавляем информацию о социальном аккаунте
        try:
            social_account = SocialAccount.objects.get(user=user)
            context['social_account'] = social_account
            context['social_provider'] = social_account.provider
        except SocialAccount.DoesNotExist:
            context['social_account'] = None
            context['social_provider'] = None
        
        return context


