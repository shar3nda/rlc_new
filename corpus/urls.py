from django.urls import path

from corpus import views

urlpatterns = [
    path("add-document/", views.add_document, name="add_document"),
    path("documents/", views.documents, name="documents"),
    path("annotate/<int:document_id>/", views.annotate, name="annotate"),
    path(
        "update_document_status/<int:document_id>/",
        views.update_document_status,
        name="update_document_status",
    ),
    path("search/", views.search, name="search"),
    path("search/results/<int:page>/", views.search_results, name="search_results"),
]
