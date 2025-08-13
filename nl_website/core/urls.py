from django.urls import path
from . import views
from django.views.generic.base import RedirectView

app_name = 'core'

urlpatterns = [
    path('', views.IndexPage.as_view(), name='home'),
    path('about/', views.AboutPage.as_view(), name='about'),
    path('profile/', RedirectView.as_view(pattern_name='account_login'), name='profile'),
]
