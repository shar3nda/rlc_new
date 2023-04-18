from django.shortcuts import render
from django.views import View

from .models import Section


class HomepageView(View):
    @staticmethod
    def get(request):
        section_list = Section.objects.order_by("number")
        page = "homepage.html"
        return render(request, page, {"sections": section_list})
