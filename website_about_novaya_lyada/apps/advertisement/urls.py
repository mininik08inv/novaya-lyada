from django.urls import path

from advertisement.views import (
    AllAdvertisement,
    AddAdvertisement,
    ShowAdvertisement,
    UpdateAdvertisement,
    DeleteAdvertisement,
)

app_name = "advertisement"

urlpatterns = [
    path("", AllAdvertisement.as_view(), name="advertisement_all"),
    path("add/", AddAdvertisement.as_view(), name="advertisement_add"),
    path("<slug:advertisement_slug>/", ShowAdvertisement.as_view(), name="advertisement_detail"),
    path("<slug:advertisement_slug>/edit/", UpdateAdvertisement.as_view(), name="advertisement_update"),
    path("<slug:advertisement_slug>/delete/", DeleteAdvertisement.as_view(), name="advertisement_delete"),
]
