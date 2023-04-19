from django.contrib import admin
from django.urls import path, include
from . import views
from .views import HomepageView

urlpatterns = [
    path("", HomepageView.as_view(), name="homepage"),
]
