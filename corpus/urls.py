from django.urls import path

from corpus import views

urlpatterns = [
    path("add_document", views.add_document, name="add_document"),
    path(
        "edit_document/<int:document_id>/",
        views.edit_document,
        name="edit_document",
    ),
    path(
        "edit_author/<int:author_id>/document/<int:document_id>/",
        views.edit_author,
        name="edit_author",
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
    path("statistics/", views.statistics, name="statistics"),
    path("help/", views.help, name="help"),
    path("export_documents/", views.export_documents, name="export_documents"),
    path("search/", views.search, name="search"),
    path("search_results/", views.search_results, name="search_results"),
    path("get_search", views.get_search, name="get_search"),
]
