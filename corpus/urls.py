from django.contrib import admin
from django.urls import path, include
from corpus import views

urlpatterns = [
    path("documents/", views.documents, name="documents"),
    path("annotate/<int:id>/", views.annotate, name="annotate"),
]
