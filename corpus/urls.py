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
    path("help/", views.help_page, name="help"),
    path("export_documents/", views.export_documents, name="export_documents"),
    path("search/", views.search, name="search"),
    path(
        "dynamic_lexgram_form", views.dynamic_lexgram_form, name="dynamic_lexgram_form"
    ),
    path(
        "lexgram_search_results/",
        views.lexgram_search_results,
        name="lexgram_search_results",
    ),
    path(
        "exact_search_results/",
        views.exact_search_results,
        name="exact_search_results",
    ),
    path("subcorpus_form/", views.subcorpus_form, name="subcorpus_form"),
]
