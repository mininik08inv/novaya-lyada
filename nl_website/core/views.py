from django.shortcuts import render
from django.views.generic import TemplateView
from events.models import Event
from advertisement.models import Advertisement


# Create your views here.
class IndexPage(TemplateView):
    template_name = 'index.html'
    extra_context = {"title": "Главная страница"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.published.all()[:3]
        context['ads'] = Advertisement.published.all()[:3]
        return context


class AboutPage(TemplateView):
    template_name = 'about.html'
    extra_context = {"title": "О сайте"}

