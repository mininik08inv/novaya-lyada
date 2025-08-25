from django.urls import path
from website_about_novaya_lyada.apps.accounts import views

app_name = 'accounts'

urlpatterns = [
    path('', views.ProfileView.as_view(), name='profile'),
]


