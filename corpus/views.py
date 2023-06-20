from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .filters import DocumentFilter
from .forms import DocumentForm, NewAuthorForm, FavoriteAuthorForm, TokenSearchForm
from .models import Document, Sentence, Author


def export_documents(request):
    document_list = Document.objects.select_related("user", "author").prefetch_related(
        "annotators", "sentence_set__annotation_set__user"
    )

    filter = DocumentFilter(request.GET, queryset=document_list)

    data = [document.serialize() for document in filter.qs]

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


def get_verbose_name(model, field_name, choice_code):
    return dict(model._meta.get_field(field_name).flatchoices).get(choice_code)


def clean_for_js(data):
    """Transforms None into a value appropriate for JavaScript"""
    return [item if item is not None else "Unknown" for item in data]


def statistics(request):
    # Aggregate the data
    status_counts = Document.objects.values("status").annotate(count=Count("status"))

    # Prepare the data for the chart
    labels = [status[1] for status in Document.StatusChoices.choices]
    text_types = []
    for status_value, status_label in Document.StatusChoices.choices:
        count = int(status_counts.get(status=status_value)["count"])
        text_types.append(count)
    texts_count = int(Document.objects.count())
    colors = ["#8c61ff", "#44c2fd", "#6592fd"]

    # Статистика по документам
    languages_counts = (
        Document.objects.values("author__dominant_language")
        .annotate(count=Count("id"))
        .order_by()
    )
    languages_counts = {
        get_verbose_name(
            Author, "dominant_language", doc["author__dominant_language"]
        ): doc["count"]
        for doc in languages_counts
    }

    gender_counts = (
        Document.objects.values("author__gender").annotate(count=Count("id")).order_by()
    )
    gender_counts = {
        get_verbose_name(Author, "gender", doc["author__gender"]): doc["count"]
        for doc in gender_counts
    }

    lang_background_counts = (
        Document.objects.values("author__language_background")
        .annotate(count=Count("id"))
        .order_by()
    )
    lang_background_counts = {
        get_verbose_name(
            Author, "language_background", doc["author__language_background"]
        ): doc["count"]
        for doc in lang_background_counts
    }

    genre_counts = (
        Document.objects.values("genre").annotate(count=Count("id")).order_by()
    )
    genre_counts = {
        get_verbose_name(Document, "genre", doc["genre"]): doc["count"]
        for doc in genre_counts
    }

    # статистика по предложениям
    lang_sent_counts = (
        Sentence.objects.values("document__author__dominant_language")
        .annotate(count=Count("id"))
        .order_by()
    )
    lang_sent_counts = {
        get_verbose_name(
            Author, "dominant_language", sent["document__author__dominant_language"]
        ): sent["count"]
        for sent in lang_sent_counts
    }

    # Статистика по авторам
    auth_gender = Author.objects.values("gender").annotate(count=Count("id")).order_by()
    auth_gender = {
        get_verbose_name(Author, "gender", auth["gender"]): auth["count"]
        for auth in auth_gender
    }

    auth_lang_bg_counts = (
        Author.objects.values("language_background")
        .annotate(count=Count("id"))
        .order_by()
    )
    auth_lang_bg_counts = {
        get_verbose_name(
            Author, "language_background", auth["language_background"]
        ): auth["count"]
        for auth in auth_lang_bg_counts
    }

    auth_lang_counts = (
        Author.objects.values("dominant_language")
        .annotate(count=Count("id"))
        .order_by()
    )
    auth_lang_counts = {
        get_verbose_name(Author, "dominant_language", auth["dominant_language"]): auth[
            "count"
        ]
        for auth in auth_lang_counts
    }

    languages_counts = dict(sorted(languages_counts.items()))
    lang_sent_counts = dict(sorted(lang_sent_counts.items()))
    # Render the chart
    table_data = list(
        zip(
            languages_counts.keys(),
            languages_counts.values(),
            lang_sent_counts.values(),
        )
    )

    # статистика по предложениям
    total_sentences = Sentence.objects.count()

    # Статистика по авторам
    total_authors = Author.objects.count()
    total_fav_authors = Author.objects.filter(favorite=True).count()

    context = {
        "labels": labels,
        "text_types": text_types,
        "colors": colors,
        "texts_count": texts_count,
        "languages_labels": clean_for_js(list(languages_counts.keys())),
        "languages_counts": list(languages_counts.values()),
        "gender_labels": clean_for_js(list(gender_counts.keys())),
        "gender_counts": list(gender_counts.values()),
        "lang_background_labels": clean_for_js(list(lang_background_counts.keys())),
        "lang_background_counts": list(lang_background_counts.values()),
        "genre_labels": clean_for_js(list(genre_counts.keys())),
        "genre_counts": list(genre_counts.values()),
        "total_sentences": total_sentences,
        "lang_sent_labels": clean_for_js(list(lang_sent_counts.keys())),
        "lang_sent_counts": list(lang_sent_counts.values()),
        "total_authors": total_authors,
        "total_fav_authors": total_fav_authors,
        "auth_gender_labels": clean_for_js(list(auth_gender.keys())),
        "auth_gender_counts": list(auth_gender.values()),
        "auth_lang_bg_labels": clean_for_js(list(auth_lang_bg_counts.keys())),
        "auth_lang_bg_counts": list(auth_lang_bg_counts.values()),
        "auth_lang_labels": clean_for_js(list(auth_lang_counts.keys())),
        "auth_lang_counts": list(auth_lang_counts.values()),
        "table_data": table_data,
    }
    return render(request, "statistics.html", context)


def help(request):
    return render(request, "help.html")


# Представление для аннотирования документа
def annotate(request, document_id):
    doc = Document.objects.get(id=document_id)
    context = {
        "document": doc,
        "sentences": Sentence.objects.filter(document=doc).order_by("number"),
    }
    return render(request, "annotate.html", context)


@permission_required("annotator.change_document")
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
                document.user = request.user
                document.author = author
                document.save()
            elif (
                request.POST["author_selection_method"] == "dropdown"
                and favorite_author_form.is_valid()
            ):
                document = form.save(commit=False)
                document.user = request.user
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
        form = DocumentForm(initial={"user": request.user.id})
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


@permission_required("corpus.change_document")
def edit_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == "POST":
        form = DocumentForm(request.POST, instance=document)
        favorite_author_form = FavoriteAuthorForm(
            request.POST, prefix="favorite_author"
        )

        if form.is_valid():
            form.save(commit=False)
            if favorite_author_form.is_valid() and favorite_author_form.cleaned_data['selected_author'] is not None:
                document.author = favorite_author_form.cleaned_data["selected_author"]
            document.save()
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



@permission_required("corpus.change_document")
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


@permission_required("corpus.delete_document")
def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    document.delete()
    messages.success(request, "Документ успешно удален!")
    return redirect("documents")


@permission_required("corpus.change_document")
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


def search(request):
    form = TokenSearchForm(request.GET)
    results = Document.objects.none()  # No results initially

    if form.is_valid() and form.cleaned_data:
        # Define the fields to be filtered on and their corresponding lookup types
        filter_fields = (
            "lemma",
            "pos",
            "animacy",
            "aspect",
            "case",
            "degree",
            "foreign",
            "gender",
            "hyph",
            "mood",
            "gram_number",
            "person",
            "polarity",
            "tense",
            "variant",
            "verb_form",
            "voice",
        )

        # Create Q objects for each filter, if a value was provided
        queries = [
            Q(**{f"token__{field}": form.cleaned_data[field]})
            for field in filter_fields
            if field in form.cleaned_data and form.cleaned_data[field]
        ]

        # Add filter by error tags if the 'errors' field was provided
        errors = form.cleaned_data.get("gram_errors")
        if errors:
            error_queries = [
                Q(annotation__error_tags__contains=[error])
                & Q(annotation__tokens__lemma=form.cleaned_data["lemma"])
                for error in errors
            ]

            errors_query = error_queries.pop()
            for error_query in error_queries:
                errors_query |= error_query  # Combine with OR, not AND
            queries.append(errors_query)

        # Combine the Q objects with the AND operator
        if queries:
            query = queries.pop()
            for item in queries:
                query &= item

            # Apply the filter
            results = Document.objects.filter(query).distinct()

    paginator = Paginator(results, 10)  # Show 10 results per page

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "lexgram_search.html", {"form": form, "page_obj": page_obj})
