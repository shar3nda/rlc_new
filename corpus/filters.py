from django.contrib.auth.models import User
from django.db.models import Q
import django_filters
from .models import Document, Author


class DocumentFilter(django_filters.FilterSet):
    author = django_filters.ModelChoiceFilter(
        queryset=Author.objects.filter(favorite=True).order_by("name"),
        label="Автор",
    )
    author_search = django_filters.CharFilter(
        method="author_search_filter",
        label="Поиск автора",
    )
    user = django_filters.ModelChoiceFilter(
        queryset=User.objects.order_by("username"),
        label="Создатель",
    )
    user_search = django_filters.CharFilter(
        method="user_search_filter",
        label="Поиск создателя",
    )
    author__language_background = django_filters.ChoiceFilter(
        field_name="author__language_background",
        choices=Author.LanguageBackgroundChoices.choices,
        lookup_expr="exact",
        label="Тип носителя",
    )
    author__dominant_language = django_filters.ChoiceFilter(
        field_name="author__dominant_language",
        choices=Author.DominantLanguageChoices.choices,
        lookup_expr="exact",
        label="Родной язык",
    )
    title = django_filters.CharFilter(
        field_name="title", lookup_expr="icontains", label="Название"
    )
    body = django_filters.CharFilter(
        field_name="body", lookup_expr="icontains", label="Текст"
    )

    def author_search_filter(self, queryset, name, value):
        return queryset.filter(author__name__icontains=value)

    def user_search_filter(self, queryset, name, value):
        return queryset.filter(user__username__icontains=value)

    class Meta:
        model = Document
        fields = {
            "date": ["exact"],
            "genre": ["exact"],
            "subcorpus": ["exact"],
            "source": ["exact"],
        }
