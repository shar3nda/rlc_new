import json

from django.http import JsonResponse
from django.shortcuts import render

from .models import Document, Annotation, Sentence


# Представление для списка документов
def documents(request):
    docs = Document.objects.all()
    context = {
        "documents": docs,
    }
    return render(request, "documents.html", context)


# Представление для аннотирования документа
def annotate(request, id):
    doc = Document.objects.get(id=id)
    context = {
        "document": doc,
        "sentences": Sentence.objects.filter(document=doc),
    }
    return render(request, "annotate.html", context)


# Представление для главной страницы
def homepage(request):
    return render(request, "homepage.html")
