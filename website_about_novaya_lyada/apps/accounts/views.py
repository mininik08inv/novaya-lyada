from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from advertisement.models import Advertisement
from django.conf import settings


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'account/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['default_image'] = getattr(settings, 'DEFAULT_USER_IMAGE', '')
        context['my_ads'] = Advertisement.objects.filter(author=user).order_by('-created')
        return context


