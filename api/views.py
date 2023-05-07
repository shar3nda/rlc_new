import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect

from corpus.models import Annotation, Document, Sentence
from corpus.views import user_profile


def get_annotations(request):
    if request.method == "GET":
        annotations = Annotation.objects.all()
        data = {"annotations": list(annotations.values())}
        return JsonResponse(data)


def get_documents(request):
    if request.method == "GET":
        documents = Document.objects.all()
        data = {"documents": list(documents.values())}
        return JsonResponse(data)


def get_sentence_annotations(request, sentence_id):
    if request.method == "GET":
        sentence_annotations = Annotation.objects.filter(
            sentence=sentence_id, alt=False
        )
        data = [annotation.json for annotation in sentence_annotations]
        return JsonResponse(data, safe=False)


def get_alt_sentence_annotations(request, sentence_id):
    if request.method == "GET":
        sentence_annotations = Annotation.objects.filter(sentence=sentence_id, alt=True)
        data = [annotation.json for annotation in sentence_annotations]
        return JsonResponse(data, safe=False)


def create_annotation(request):
    if request.method == "POST":
        data = json.loads(request.body)
        annotation = Annotation.objects.create(
            sentence=Sentence.objects.get(id=data["sentence"]),
            document=Document.objects.get(id=data["document"]),
            user=User.objects.get(id=data["user"]),
            guid=data["guid"],
            alt=True if data["alt"] == "true" else False,
            json=data["body"],
        )
        return JsonResponse({"id": annotation.id})


def update_annotation(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        annotation_id = json.loads(request.body)["guid"]
        annotation = Annotation.objects.get(guid=annotation_id)
        annotation.json = data["body"]
        annotation.save()
        return JsonResponse({"id": annotation.id})


def delete_annotation(request):
    if request.method == "DELETE":
        annotation_id = json.loads(request.body)["guid"]
        annotation = Annotation.objects.get(guid=annotation_id)
        annotation.delete()
        return JsonResponse({"id": annotation_id})


def get_new_id(request):
    if request.method == "GET":
        new_id = 1
        if Annotation.objects.count() > 0:
            new_id = Annotation.objects.last().id + 1
        data = {"id": new_id}
        return JsonResponse(data)


def get_sentence_corrections(request, sentence_id):
    if request.method == "GET":
        sentence = Sentence.objects.get(id=sentence_id)
        data = {
            "correction": sentence.correction,
            "alt_correction": sentence.alt_correction,
        }
        return JsonResponse(data)


def get_user_info(request):
    if request.method == "GET":
        user = User.objects.get(id=request.user.id)
        data = {
            "id": redirect(user_profile).url,
            "displayName": user.username,
        }
        return JsonResponse(data)
