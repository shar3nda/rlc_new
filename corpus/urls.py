from django.contrib import admin
from django.urls import path, include
from corpus import views

urlpatterns = [
    path("add-document/", views.add_document, name="add_document"),
    path("documents/", views.documents, name="documents"),
    path("annotate/<int:document_id>/", views.annotate, name="annotate"),
]
