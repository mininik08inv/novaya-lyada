from django.urls import path, reverse_lazy

from about_village import views

app_name = "about_village"

urlpatterns = [
    path('', views.AboutVillage.as_view(), name='about_village'),
    path('famous-persons/', views.FamousPeopleAll.as_view(), name='famous_person_all'),
    path('persons/<slug:person_slug>/', views.PersonDetail.as_view(), name='person_detail'),



    # path('event/<slug:event_slug>/', views.ShowEvent.as_view(), name='event_detail'),
    # path('event_update/<slug:event_slug>/', views.UpdateEvent.as_view(), name='event_update'),
    # path('add_event/', views.AddEvent.as_view(), name='add_event'),
    # path('event_delete/<slug:event_slug>/', views.ShowEvent.as_view(), name='event_delete'),
]
