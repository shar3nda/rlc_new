from django.contrib.auth.models import User
import django_filters
from .models import Document, Author, Annotation


class DocumentFilter(django_filters.FilterSet):
    author = django_filters.ChoiceFilter(
        field_name="author",
        choices=Author.objects.filter(favorite=True)
        .values_list("id", "name")
        .order_by("name"),
        lookup_expr="exact",
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
    author__name = django_filters.CharFilter(
        field_name="author__name", lookup_expr="icontains", label="Автор"
    )
    user__username = django_filters.CharFilter(
        field_name="user__username", lookup_expr="exact", label="Создатель"
    )
    annotator = django_filters.ModelChoiceFilter(
        field_name="annotators",
        queryset=User.objects.order_by("username"),
        to_field_name="id",
        label="Разметчик",
        distinct=True,
    )
    status = django_filters.ChoiceFilter(
        field_name="status",
        choices=Document.StatusChoices.choices,
        lookup_expr="exact",
        label="Статус",
    )


    class Meta:
        model = Document
        fields = {
            "date": ["exact"],
            "genre": ["exact"],
            "subcorpus": ["exact"],
            "source": ["exact"],
            "user": ["exact"],
        }
