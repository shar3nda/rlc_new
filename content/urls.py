from django.contrib import admin
from django.urls import path, include
from . import views
from .views import HomepageView

urlpatterns = [
    path("", HomepageView.as_view(), name="homepage"),
    path("news/", views.NewsView.as_view(), name="news"),
    path("create_article/", views.article_create_view, name="create_article"),
    path("delete_article/<int:pk>/", views.delete_article, name="delete_article"),
]
