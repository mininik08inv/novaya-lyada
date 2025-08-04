from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.
class IndexPage(TemplateView):
    template_name = 'index.html'
    extra_context = {"title": "Главная страница"}


class AboutPage(TemplateView):
    template_name = 'about.html'
    extra_context = {"title": "О сайте"}
