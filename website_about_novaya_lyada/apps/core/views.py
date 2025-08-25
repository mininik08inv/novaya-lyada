from django.shortcuts import render
from django.views.generic import TemplateView
from website_about_novaya_lyada.apps.events.models import Event
from website_about_novaya_lyada.apps.advertisement.models import Advertisement
from website_about_novaya_lyada.apps.ideas.models import ImprovementIdea


# Create your views here.
class IndexPage(TemplateView):
    template_name = 'index.html'
    extra_context = {"title": "Главная страница"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.published.all()[:3]
        context['ads'] = Advertisement.published.all()[:3]
        context['ideas'] = ImprovementIdea.objects.filter(
            status__in=['collection', 'pending', 'approved', 'implemented']
        ).order_by('-created_at')[:3]
        return context


class AboutPage(TemplateView):
    template_name = 'about.html'
    extra_context = {"title": "О сайте"}


class PrivacyPage(TemplateView):
    template_name = 'privacy.html'
    extra_context = {"title": "Политика конфиденциальности"}


class TermsPage(TemplateView):
    template_name = 'terms.html'
    extra_context = {"title": "Условия использования"}

