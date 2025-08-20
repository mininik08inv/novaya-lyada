from django.urls import path
from . import views

app_name = "ideas"

urlpatterns = [
    path('', views.AllIdeas.as_view(), name='all_ideas'),
    path('idea/<slug:idea_slug>/', views.IdeaDetail.as_view(), name='idea_detail'),
    path('add/', views.AddIdea.as_view(), name='add_idea'),
    path('<slug:idea_slug>/add-comment/', views.AddComment.as_view(), name='add_comment'),
    path('<slug:idea_slug>/vote/', views.VoteIdea.as_view(), name='vote_idea'),
]
