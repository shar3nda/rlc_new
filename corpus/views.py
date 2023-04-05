import json

from django.http import JsonResponse
from django.shortcuts import render

from .models import Document, Annotation


# Представление для списка документов
def document_list(request):
    documents = Document.objects.all()
    context = {
        "documents": documents,
    }
    return render(request, "documents.html", context)


# Представление для аннотирования документа
def annotate(request, id):
    doc = Document.objects.get(id=id)
    context = {
        "document": doc,
    }
    return render(request, "annotate.html", context)


# Представление для главной страницы
def homepage(request):
    return render(request, "homepage.html")


"""
{
  "@context": "http://www.w3.org/ns/anno.jsonld",
  "type": "Annotation",
  "body": [
    {
      "type": "TextualBody",
      "value": "test",
      "purpose": "commenting"
    }
  ],
  "target": {
    "selector": [
      {
        "type": "TextQuoteSelector",
        "exact": "\ud83d\ude34\ud83d\ude34\ud83d\ude34"
      },
      {
        "type": "TextPositionSelector",
        "start": 7,
        "end": 13
      }
    ]
  },
  "id": "#cbf633ee-d989-4e66-950e-83cb3abc8aa9"
}
"""


def update_model(request):
    # get the data from the request as a JSON object
    json_response = request.body.decode("utf-8")
    data = json.loads(json_response)
    CREATE_ANNOT, UPDATE_ANNOT, DELETE_ANNOT = 0, 1, 2
    response = {"success": True, "message": "Model updated successfully"}
    if data["action"] == CREATE_ANNOT:
        Annotation.objects.create(
            document_id=data["document_id"],
            user_id=data["user_id"],
            exact_selector=data["target"]["selector"][0]["exact"],
            start_selector=data["target"]["selector"][1]["start"],
            end_selector=data["target"]["selector"][1]["end"],
            value=data["body"][0]["value"],
            # TODO: generate ID on the server and override it
            recogito_id=data["id"],
            json=json_response,
        )
        response["id"] = Annotation.objects.last().id
    elif data["action"] == UPDATE_ANNOT:
        # TODO update the annotation with the given id
        # TODO handle annotation replies
        Annotation.objects.filter(recogito_id=data["id"]).update(
            user_id=data["user_id"],
            exact_selector=data["exact_selector"],
            start_selector=data["start_selector"],
            end_selector=data["end_selector"],
            value=data["value"],
            json=data["json"],
        )
    elif data["action"] == DELETE_ANNOT:
        Annotation.objects.filter(id=data["id"]).delete()
    return JsonResponse(response, safe=False)


def get_annotations(request, id):
    annotations = Annotation.objects.filter(document_id=id)
    response = []
    for annotation in annotations:
        response.append(json.loads(annotation.json))
    return JsonResponse(response, safe=False)
