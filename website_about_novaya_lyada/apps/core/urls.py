from django.urls import path
from website_about_novaya_lyada.apps.core import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexPage.as_view(), name='home'),
    path('about/', views.AboutPage.as_view(), name='about'),
    path('privacy/', views.PrivacyPage.as_view(), name='privacy'),
    path('terms/', views.TermsPage.as_view(), name='terms'),
]
