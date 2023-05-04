from django.contrib.auth.models import User
import django_filters
from .models import Document, Author


class DocumentFilter(django_filters.FilterSet):
    author = django_filters.ChoiceFilter(
        field_name="author",
        choices=Author.objects.filter(favorite=True).values_list("id", "name"),
        lookup_expr="exact",
    )
    username = django_filters.ChoiceFilter(
        field_name="user__username",
        choices=User.objects.values_list("username", "username"),
        lookup_expr="exact",
        label="Пользователь",
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

    class Meta:
        model = Document
        fields = {
            "date": ["exact"],
            "genre": ["exact"],
            "subcorpus": ["exact"],
            "source": ["exact"],
        }