from django.contrib import admin

from corpus.models import Author


class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "gender",
        "program",
        "language_background",
        "dominant_language",
        "language_level",
        "favorite",
    )
    list_filter = ("favorite",)  # Enable filtering by 'favorite'
    search_fields = ("name",)  # Enable search by 'name'

    fieldsets = (
        (None, {"fields": ("name", "gender", "program", "language_background")}),
        ("Язык", {"fields": ("dominant_language", "language_level")}),
        ("Доп. опции", {"fields": ("favorite",)}),
    )


admin.site.register(Author, AuthorAdmin)
