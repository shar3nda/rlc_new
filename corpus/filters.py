import django_filters
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Document, Author, Token


class DocumentFilter(django_filters.FilterSet):
    def body_search(self, queryset, name, value):
        return queryset.filter(body__search=value)

    author = django_filters.ChoiceFilter(
        field_name="author",
        choices=Author.objects.filter(favorite=True)
        .values_list("id", "name")
        .order_by("name"),
        lookup_expr="exact",
        label=_("Author"),
    )
    author_search = django_filters.CharFilter(
        method="author_search_filter",
        label=_("Author search"),
    )
    user = django_filters.ModelChoiceFilter(
        queryset=User.objects.order_by("username"),
        label=_("Owner"),
    )
    user_search = django_filters.CharFilter(
        method="user_search_filter",
        label=_("Owner search"),
    )
    author__language_background = django_filters.ChoiceFilter(
        field_name="author__language_background",
        choices=Author.LanguageBackgroundChoices.choices,
        lookup_expr="exact",
        label=_("Language background"),
    )
    author__dominant_language = django_filters.ChoiceFilter(
        field_name="author__dominant_language",
        choices=Author.DominantLanguageChoices.choices,
        lookup_expr="exact",
        label=_("Dominant language"),
    )
    title = django_filters.CharFilter(
        field_name="title", lookup_expr="icontains", label=_("Title")
    )
    body = django_filters.CharFilter(method="body_search", label=_("Text"))
    author__name = django_filters.CharFilter(
        field_name="author__name", lookup_expr="icontains", label=_("Author")
    )
    language_level = django_filters.ChoiceFilter(
        field_name="language_level",
        choices=Document.LanguageLevelChoices.choices,
        lookup_expr="exact",
        label=_("Language level"),
    )
    user__username = django_filters.CharFilter(
        field_name="user__username", lookup_expr="exact", label=_("Owner")
    )
    annotator = django_filters.ModelChoiceFilter(
        field_name="annotators",
        queryset=User.objects.order_by("username"),
        to_field_name="id",
        label=_("Annotator"),
        distinct=True,
    )
    status = django_filters.ChoiceFilter(
        field_name="status",
        choices=Document.StatusChoices.choices,
        lookup_expr="exact",
        label=_("Status"),
    )

    class Meta:
        model = Document
        fields = {
            "date": ["exact"],
            "genre": ["exact"],
            "subcorpus": ["exact"],
            "language_level": ["exact"],
            "user": ["exact"],
        }
