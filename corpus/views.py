from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core import serializers
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Count

from .filters import DocumentFilter
from .forms import DocumentForm, NewAuthorForm, FavoriteAuthorForm
from .models import Document, Sentence, Author


def export_documents(request):
    # Get the current queryset based on the search parameters in the request
    document_list = Document.objects.all()
    filter = DocumentFilter(request.GET, queryset=document_list)

    # Serialize the filtered documents to JSON
    data = [document.serialize() for document in filter.qs]

    # Create the JsonResponse object with the appropriate JSON header
    response = JsonResponse(data, safe=False)
    response["Content-Disposition"] = 'attachment; filename="documents.json"'

    return response


def documents(request):
    document_filter = DocumentFilter(request.GET, queryset=Document.objects.all())
    paginator = Paginator(document_filter.qs, 10)  # Show 10 documents per page.

    page = request.GET.get("page")
    try:
        docs = paginator.page(page)
    except PageNotAnInteger:
        docs = paginator.page(1)
    except EmptyPage:
        docs = paginator.page(paginator.num_pages)

    context = {
        "documents": docs,
        "filter": document_filter,
        "body_query": request.GET.get("body", ""),
        "title_query": request.GET.get("title", ""),
    }
    return render(request, "documents.html", context)


def statistics(request):
    # Aggregate the data
    status_counts = Document.objects.values("status").annotate(count=Count("status"))

    # Prepare the data for the chart
    labels = [status[1] for status in Document.StatusChoices.choices]
    text_types = []
    for status_value, status_label in Document.StatusChoices.choices:
        count = int(status_counts.get(status=status_value)["count"])
        text_types.append(count)
    texts_count = int(Document.objects.all().count())
    colors = ["#8c61ff", "#44c2fd", "#6592fd"]

    # Статистика по документам
    languages_counts = defaultdict(int)
    gender_counts = defaultdict(int) # количество текстов с женским авторством, НЕ количество женщин авторов
    lang_background_counts = defaultdict(int)
    genre_counts = defaultdict(int)
    for doc in Document.objects.all():
        languages_counts[doc.author.get_dominant_language_display()] += 1
        gender_counts[doc.author.get_gender_display()] += 1
        lang_background_counts[doc.author.get_language_background_display()] += 1
        genre_counts[doc.get_genre_display()] += 1

    # статистика по предложениям
    total_sentences = 0
    lang_sent_counts = defaultdict(int)
    for sent in Sentence.objects.all():
        lang_sent_counts[sent.document.author.get_dominant_language_display()] += 1
        total_sentences += 1

    total_authors = 0
    total_fav_authors = 0
    auth_gender = defaultdict(int)
    # Статистика по авторам
    for author in Author.objects.all():
        total_authors += 1
        if author.favorite:
            total_fav_authors += 1

    languages_counts = dict(sorted(languages_counts.items()))
    lang_sent_counts = dict(sorted(lang_sent_counts.items()))
    # Render the chart
    table_data = list(zip(languages_counts.keys(), languages_counts.values(), lang_sent_counts.values()))
    print(table_data)
    context = {'labels': labels,
               'text_types': text_types,
               'colors': colors,
               'texts_count': texts_count,
               'languages_labels': list(languages_counts.keys()),
               'languages_counts': list(languages_counts.values()),
               'gender_labels': list(gender_counts.keys()),
               'gender_counts': list(gender_counts.values()),
               'lang_background_labels': list(lang_background_counts.keys()),
               'lang_background_counts': list(lang_background_counts.values()),
               'genre_labels': list(genre_counts.keys()),
               'genre_counts': list(genre_counts.values()),
               'total_sentences': total_sentences,
               'lang_sent_labels': list(lang_sent_counts.keys()),
               'lang_sent_counts': list(lang_sent_counts.values()),
               'total_authors': total_authors,
               'total_fav_authors': total_fav_authors,
               'table_data': table_data,
               }
    return render(request, 'statistics.html', context)


@login_required
# Представление для аннотирования документа
def annotate(request, document_id):
    doc = Document.objects.get(id=document_id)
    context = {
        "document": doc,
        "sentences": Sentence.objects.filter(document=doc).order_by("number"),
    }
    return render(request, "annotate.html", context)


@login_required
def add_document(request):
    if request.method == "POST":
        form = DocumentForm(request.POST)
        author_form = NewAuthorForm(request.POST, prefix="author")
        favorite_author_form = FavoriteAuthorForm(
            request.POST, prefix="favorite_author"
        )

        if form.is_valid():
            if (
                request.POST["author_selection_method"] == "manual"
                and author_form.is_valid()
            ):
                author = author_form.save()
                document = form.save(commit=False)
                document.author = author
                document.save()
            elif (
                request.POST["author_selection_method"] == "dropdown"
                and favorite_author_form.is_valid()
            ):
                document = form.save(commit=False)
                document.author = favorite_author_form.cleaned_data["selected_author"]
                document.save()
            else:
                messages.error(
                    request,
                    "Invalid author information. Please check the form and try again.",
                )
                return redirect("add_document")

            messages.success(request, "Document saved successfully.")
            return redirect("annotate", document_id=document.id)
        else:
            messages.error(
                request,
                "An error occurred while saving the document. Please check the form and try again.",
            )
            return redirect("add_document")
    else:
        form = DocumentForm()
        author_form = NewAuthorForm(prefix="author")
        favorite_author_form = FavoriteAuthorForm(prefix="favorite_author")

    return render(
        request,
        "add_document.html",
        {
            "form": form,
            "author_form": author_form,
            "favorite_author_form": favorite_author_form,
        },
    )


@login_required
def edit_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == "POST":
        form = DocumentForm(request.POST, instance=document)
        favorite_author_form = FavoriteAuthorForm(
            request.POST, prefix="favorite_author"
        )

        if form.is_valid():
            form.save(commit=False)
            if favorite_author_form.is_valid():
                document.author = favorite_author_form.cleaned_data["selected_author"]
                document.save()
            else:
                messages.error(
                    request,
                    "Не удалось сохранить автора. Пожалуйста, проверьте форму и попробуйте снова.",
                )
                return redirect("edit_document", document_id=document_id)
            return redirect("annotate", document_id=document.id)
        else:
            messages.error(
                request,
                "Во время сохранения документа произошла ошибка. Пожалуйста, проверьте форму и попробуйте снова.",
            )
            return redirect("edit_document", document_id=document_id)
    else:
        form = DocumentForm(instance=document)
        if document.author.favorite:
            favorite_author_form = FavoriteAuthorForm(
                prefix="favorite_author", initial={"selected_author": document.author}
            )
        else:
            favorite_author_form = FavoriteAuthorForm(prefix="favorite_author")

    return render(
        request,
        "edit_document.html",
        {
            "form": form,
            "document": document,
            "favorite_author_form": favorite_author_form,
        },
    )


@login_required
def edit_author(request, author_id, document_id):
    author = get_object_or_404(Author, id=author_id)
    if request.method == "POST":
        form = NewAuthorForm(request.POST, instance=author, prefix="author")

        if form.is_valid():
            form.save()
            messages.success(request, "Author saved successfully.")
            return redirect("edit_document", document_id=document_id)
        else:
            messages.error(
                request,
                "An error occurred while saving the author. Please check the form and try again.",
            )
            return redirect("edit_author", author_id=author_id, document_id=document_id)
    else:
        form = NewAuthorForm(instance=author, prefix="author")

    return render(
        request,
        "edit_author.html",
        {
            "author_form": form,
            "author": author,
            "document": get_object_or_404(Document, id=document_id),
        },
    )


def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    document.delete()
    messages.success(request, "Документ успешно удален!")
    return redirect("documents")


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"


def update_document_status(request, document_id):
    if request.method == "POST":
        status = request.POST.get("status")
        document = get_object_or_404(Document, id=document_id)
        document.status = int(status)
        document.save()
        messages.success(request, "Статус документа успешно обновлен!")
        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"status": "error"})


@login_required
def user_profile(request):
    return render(request, "user_profile.html", {"user": request.user})
