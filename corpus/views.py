from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from .filters import DocumentFilter
from .forms import DocumentForm, NewAuthorForm, FavoriteAuthorForm
from .models import Document, Sentence, Author


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
