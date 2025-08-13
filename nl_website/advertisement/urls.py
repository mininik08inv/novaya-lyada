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
    path("advertisement_add/", AddAdvertisement.as_view(), name="advertisement_add"),
    path(
        "advertisement/<slug:advertisement_slug>/",
        ShowAdvertisement.as_view(),
        name="advertisement_detail",
    ),
    path(
        "advertisement_update/<slug:advertisement_slug>/",
        UpdateAdvertisement.as_view(),
        name="advertisement_update",
    ),
    path(
        "advertisement_delete/<slug:advertisement_slug>/",
        DeleteAdvertisement.as_view(),
        name="advertisement_delete",
    ),
]
