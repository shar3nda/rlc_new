from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from .filters import DocumentFilter
from .forms import DocumentForm
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
        "sentences": Sentence.objects.filter(document=doc),
    }
    return render(request, "annotate.html", context)


@login_required
def add_document(request):
    if request.method == "POST":
        form = DocumentForm(request.POST)
        if form.is_valid():
            # add user to the form
            form.instance.user = request.user

            if form.data["author_selection_method"] == "manual":
                author = Author.objects.create(
                    name=form.data["author_name"],
                    gender=form.data["author_gender"],
                    program=form.data["author_program"],
                    language_background=form.data["author_language_background"],
                    dominant_language=form.data["author_dominant_language"],
                    language_level=form.data["author_language_level"],
                    # if add_to_favorites is in form
                    favorite="add_to_favorites" in form.data
                             and form.data["add_to_favorites"] == "on",
                )
            else:
                # get an existing author
                author = Author.objects.get(id=form.data["selected_author"])
            # add author to the form
            form.instance.author = author
            new_document = form.save(commit=False)
            new_document.user = request.user
            new_document.save()
            messages.success(request, "Document added successfully!")
            return redirect("annotate", document_id=new_document.id)
        else:
            messages.error(
                request,
                "There was an error adding the document. Please check your input.",
            )
    else:
        form = DocumentForm()

    context = {
        "form": form,
        "authors": Author.objects.filter(favorite=True),
    }
    return render(request, "add_document.html", context)


def update_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == "POST":
        form = DocumentForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, "Document updated successfully!")
            return redirect("annotate", document_id=document.id)
        else:
            messages.error(
                request,
                "There was an error updating the document. Please check your input.",
            )
    else:
        form = DocumentForm(instance=document)

    context = {
        "form": form,
        "authors": Author.objects.filter(favorite=True),
    }
    return render(request, "update_document.html", context)


def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    document.delete()
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
        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"status": "error"})


@login_required
def user_profile(request):
    return render(request, 'user_profile.html', {'user': request.user})
