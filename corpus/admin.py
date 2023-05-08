from django.contrib import admin

from corpus.models import Author, Document


class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "gender",
        "program",
        "language_background",
        "dominant_language",
        "source",
        "favorite",
    )
    list_filter = ("favorite",)  # Enable filtering by 'favorite'
    search_fields = ("name",)  # Enable search by 'name'

    fieldsets = (
        (None, {"fields": ("name", "gender", "program", "language_background")}),
        ("Язык", {"fields": ("dominant_language", "source")}),
        ("Доп. опции", {"fields": ("favorite",)}),
    )


class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "date",
        "genre",
        "subcorpus",
        "time_limit",
        "oral",
        "language_level",
    )
    list_filter = ("genre", "subcorpus", "time_limit", "oral", "language_level")
    search_fields = ("title", "body")

    fieldsets = (
        (None, {"fields": ("title", "date", "genre", "subcorpus")}),
        ("Текст", {"fields": ("body",)}),
        ("Доп. опции", {"fields": ("time_limit", "oral", "language_level")}),
    )


admin.site.register(Author, AuthorAdmin)
admin.site.register(Document, DocumentAdmin)
