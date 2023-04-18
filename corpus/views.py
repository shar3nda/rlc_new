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
def annotate(request, sentence_id):
    doc = Document.objects.get(id=sentence_id)
    context = {
        "document": doc,
        "sentences": Sentence.objects.filter(document=doc),
    }
    return render(request, "annotate.html", context)

