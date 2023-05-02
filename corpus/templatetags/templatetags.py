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
    highlighted = text.replace(search_text, f"<mark>{search_text}</mark>")
    return mark_safe(highlighted)
