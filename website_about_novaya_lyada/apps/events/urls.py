from django.urls import path, reverse_lazy

from . import views

app_name = "events"

urlpatterns = [
    path('', views.events, name='events_all'),
    path('event/<slug:event_slug>/', views.ShowEvent.as_view(), name='event_detail'),
    path('event_update/<slug:event_slug>/', views.UpdateEvent.as_view(), name='event_update'),
    path('add_event/', views.AddEvent.as_view(), name='add_event'),
]
