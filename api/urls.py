from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path(
        "annotations/get/<int:sentence_id>/",
        views.get_sentence_annotations,
        name="get_sentence_annotations",
    ),
    path(
        "annotations/get/alt/<int:sentence_id>/",
        views.get_alt_sentence_annotations,
        name="get_alt_sentence_annotations",
    ),
    path("annotations/create/", views.create_annotation, name="create_annotation"),
    path("annotations/update/", views.update_annotation, name="update_annotation"),
    path("annotations/delete/", views.delete_annotation, name="delete_annotation"),
    path("get_corrections/<int:sentence_id>/", views.get_sentence_corrections, name="get_sentence_corrections"),
]
