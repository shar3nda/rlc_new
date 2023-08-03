import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _

from .filters import DocumentFilter
from .forms import DocumentForm, NewAuthorForm, FavoriteAuthorForm
from .models import Document, Sentence, Author, Filter, Token_list, Token


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
    return render(request, "document/annotate.html", context)


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
        "document/add_document.html",
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
            if (
                favorite_author_form.is_valid()
                and favorite_author_form.cleaned_data["selected_author"] is not None
            ):
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
        "document/edit_document.html",
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
        "document/edit_author.html",
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
    return render(request, "lexgram/lexgram_search.html")


always_true = ~Q(pk__in=[])


def search_subcorpus(filters):
    date_from_specified = filters.date_from != 0
    date_to_specified = filters.date_to != 9999

    if date_from_specified or date_to_specified:
        # Exclude documents with unspecified dates if at least one date filter is specified
        subcorpus = Document.objects.filter(
            Q(date__gte=filters.date_from, date__lte=filters.date_to)
            & ~Q(date=None)  # Exclude documents with date=None
        )
    else:
        # Include all documents if both date filters are not specified
        subcorpus = Document.objects.all()

    # Apply other filters
    subcorpus = subcorpus.filter(
        Q(always_true if filters.gender == "any" else Q(author__gender=filters.gender))
        & Q(always_true if filters.oral == "any" else Q(oral=(filters.oral == "true")))
        & Q(
            always_true
            if filters.language_background == "any"
            else Q(author__language_background=filters.language_background)
        )
        & Q(
            always_true
            if filters.dominant_languages == [""]
            else Q(author__dominant_language__in=filters.dominant_languages)
        )
        & Q(
            always_true
            if filters.language_level == [""]
            else Q(language_level__in=filters.language_level)
        )
    )

    subcorpus_stats = {
        "documents": subcorpus.count(),
        "sentences": Sentence.objects.filter(document__in=subcorpus).count(),
        "tokens": Token.objects.filter(document__in=subcorpus).count(),
    }

    # get all sentences in subcorpus
    sentences = Sentence.objects.filter(document__in=subcorpus)

    return sentences, subcorpus_stats


def search_sentences(tokens_list, filters):
    sentences, subcorpus_stats = search_subcorpus(filters)

    tokens_list.wordform = [word.lower() for word in tokens_list.wordform]

    sentences = sentences.filter(lemmas__contains=tokens_list.wordform)

    matching_sentence_pks = []
    for sentence in sentences:
        tokens = sentence.lemmas
        for i in range(len(tokens)):
            if tokens[i] == tokens_list.wordform[0]:
                flag = True
                for j in range(1, len(tokens_list.wordform)):
                    if flag:
                        flag = any(
                            tokens[i + k] == tokens_list.wordform[j]
                            for k in range(
                                int(tokens_list.begin[j - 1]),
                                int(tokens_list.end[j - 1]) + 1,
                            )
                        )
                    else:
                        break
                if flag:
                    matching_sentence_pks.append(sentence.pk)

    matching_sentences = Sentence.objects.filter(pk__in=matching_sentence_pks)
    return matching_sentences, subcorpus_stats


def get_search_stats(sentences, subcorpus_stats):
    """
    A function that returns statistics for the search results.
    For example:
    Corpus total: 11758 documents, 190394 sentences, 2284839 words.
    Search executed in a user-defined subcorpus of 11758 documents, 190311 sentences, 2284975 words.
    Found: 0 documents, 0 contexts.
    :param sentences: found sentences
    :param subcorpus_stats: stats for the subcorpus
    :return: dict with stats
    """

    total_documents = Document.objects.count()
    total_sentences = Sentence.objects.count()
    total_tokens = Token.objects.count()

    found_documents = Document.objects.filter(
        id__in=sentences.values_list("document_id", flat=True).distinct()
    ).count()
    found_sentences = sentences.count()
    found_tokens = Token.objects.filter(sentence__in=sentences).count()

    return {
        "total_documents": total_documents,
        "total_sentences": total_sentences,
        "total_tokens": total_tokens,
        "subcorpus_documents": subcorpus_stats["documents"],
        "subcorpus_sentences": subcorpus_stats["sentences"],
        "subcorpus_tokens": subcorpus_stats["tokens"],
        "found_documents": found_documents,
        "found_sentences": found_sentences,
        "found_tokens": found_tokens,
    }


def search_results(request):
    begin = request.GET.get("from[]")
    end = request.GET.get("to[]")
    if begin is not None:
        begin = begin.split(",")
    if end is not None:
        end = end.split(",")
    tokens_list = Token_list(
        request.GET.get("wordform[]").split(","),
        begin,
        end,
    )
    filters = Filter(
        request.GET.get("date1"),
        request.GET.get("date2"),
        request.GET.get("gender"),
        request.GET.get("mode"),
        request.GET.get("background"),
        request.GET.get("language[]", "").split(","),
        request.GET.get("level[]", "").split(","),
    )

    sentences, subcorpus_stats = search_sentences(tokens_list, filters)
    stats = get_search_stats(sentences, subcorpus_stats)
    stat_names = {
        "total_documents": _("Total Documents"),
        "total_sentences": _("Total Sentences"),
        "total_tokens": _("Total Tokens"),
        "subcorpus_documents": _("Subcorpus Documents"),
        "subcorpus_sentences": _("Subcorpus Sentences"),
        "subcorpus_tokens": _("Subcorpus Tokens"),
        "found_documents": _("Found Documents"),
        "found_sentences": _("Found Sentences"),
        "found_tokens": _("Found Tokens"),
    }

    # replace keys in the stats variable with translated values
    stats = {stat_names[key]: value for key, value in stats.items()}

    return render(
        request,
        "lexgram/lexgram_search_results.html",
        {"sentences": sentences, "stats": stats},
    )


def get_search(request):
    return render(
        request,
        "partials/lexgram/lexgram_form_contents.html",
        {"block_id": uuid.uuid4()},
    )
