import re
from urllib.parse import urlencode

from django import template
from django.http import QueryDict
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def highlight_search(text, search_text):
    if not search_text:
        return text

    search_text = escape(search_text)
    highlighted = re.sub(
        f"({search_text})", f"<mark>\\1</mark>", text, flags=re.IGNORECASE
    )
    return mark_safe(highlighted)


@register.filter
def update_page_number(query_params, page_number):
    query_dict = QueryDict(query_params, mutable=True)
    query_dict["page"] = page_number
    return query_dict.urlencode()


@register.filter(name="zip")
def zip_lists(a, b):
    return zip(a, b)


@register.inclusion_tag("paginator.html")
def paginator(page_obj, request):
    query_dict = request.GET.copy()
    if "page" in query_dict:
        query_dict.pop("page")

    base_url = request.path
    query_string = urlencode(query_dict)

    return {
        "page_obj": page_obj,
        "base_url": base_url,
        "query_string": query_string,
    }


@register.filter
def split_dict_items(dictionary):
    items = list(dictionary.items())
    chunk_size = (len(items) + 2) // 3  # Round up to the nearest integer division
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
