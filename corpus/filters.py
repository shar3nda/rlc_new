import django_filters
from django import forms
from django.db.models import Q

from .models import Document


class DocumentFilter(django_filters.FilterSet):
    class Meta:
        model = Document
        fields = {
            "subcorpus": ["exact"],
            "author__language_background": ["exact"],
            "genre": ["exact"],
        }

    query = django_filters.CharFilter(method="search_query", label="Запрос")

    def search_query(self, queryset, name, value):
        in_body = self.data.get("in_body", False)

        if value:
            if in_body:
                return queryset.filter(body__icontains=value)
            else:
                return queryset.filter(title__icontains=value)
        return queryset
