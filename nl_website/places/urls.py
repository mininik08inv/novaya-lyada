from django.urls import path, reverse_lazy

from . import views

app_name = "places"

urlpatterns = [
    path('', views.AllPlaces.as_view(), name='all_places'),
    path('place/<slug:place_slug>/', views.PlaceDetail.as_view(), name='place_detail'),
    path('<slug:place_slug>/add-review/', views.PlaceAddReview.as_view(), name='add_review'),
]
