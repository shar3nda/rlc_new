from django.urls import path

from corpus import views

urlpatterns = [
    path("add_document", views.add_or_edit_document, name="add_document"),
    path(
        "edit_document/<int:document_id>/",
        views.add_or_edit_document,
        name="edit_document",
    ),
    path(
        "delete_document/<int:document_id>/",
        views.delete_document,
        name="delete_document",
    ),
    path("documents/", views.documents, name="documents"),
    path("annotate/<int:document_id>/", views.annotate, name="annotate"),
    path(
        "update_document_status/<int:document_id>/",
        views.update_document_status,
        name="update_document_status",
    ),
    path("user_profile/", views.user_profile, name="user_profile"),
]
