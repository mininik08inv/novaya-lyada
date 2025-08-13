from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexPage.as_view(), name='home'),
    path('about/', views.AboutPage.as_view(), name='about'),
]
