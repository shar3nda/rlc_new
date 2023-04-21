from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import DocumentForm
from .models import Document, Sentence, Author


# Представление для списка документов
def documents(request):
    docs = Document.objects.all()
    context = {
        "documents": docs,
    }
    return render(request, "documents.html", context)


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

            # extract the author from the form
            if form.data["add_to_favorites"] == "on":
                author = Author.objects.create(
                    name=form.data["author_name"],
                    gender=form.data["author_gender"],
                    program=form.data["author_program"],
                    language_background=form.data["author_language_background"],
                    dominant_language=form.data["author_dominant_language"],
                    language_level=form.data["author_language_level"],
                    favorite=form.data["add_to_favorites"] == "on",
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
