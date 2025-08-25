from django.urls import path
from website_about_novaya_lyada.apps.advertisement import views

app_name = "advertisement"

urlpatterns = [
    path("", views.AllAdvertisement.as_view(), name="advertisement_all"),
    path("add/", views.AddAdvertisement.as_view(), name="advertisement_add"),
    path("<slug:advertisement_slug>/", views.ShowAdvertisement.as_view(), name="advertisement_detail"),
    path("<slug:advertisement_slug>/edit/", views.UpdateAdvertisement.as_view(), name="advertisement_update"),
    path("<slug:advertisement_slug>/delete/", views.DeleteAdvertisement.as_view(), name="advertisement_delete"),
]
