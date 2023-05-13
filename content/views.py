from django.shortcuts import render, redirect
from django.views import View

from .forms import ArticleForm
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


def article_create_view(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            print("valid")
            form.save()
        else:
            print("not valid")
    else:
        form = ArticleForm()

    return render(request, "create_article.html", {"form": form})


def delete_article(request, pk):
    article = Article.objects.get(pk=pk)
    article.delete()
    return redirect('news')
