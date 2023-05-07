from django.shortcuts import render
from django.views import View

from .models import Section, Article


class HomepageView(View):
    @staticmethod
    def get(request):

        section_list = Section.objects.order_by("number")
        page = "homepage.html"
        return render(request, page, {"sections": section_list})


class NewsView(View):
    @staticmethod
    def get(request):
        articles_list = Article.objects.order_by("date")
        page = "news.html"
        return render(request, page, {"articles": articles_list})
