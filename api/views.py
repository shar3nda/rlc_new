from datetime import datetime
from typing import List, Dict
from uuid import uuid4

from django.shortcuts import redirect, get_object_or_404
from enchant import Dict as EnchantDict

from auto_annotator.annotator import Annotator

_ANNOTATOR = Annotator()
_DICTIONARY = EnchantDict("ru_RU")

from ninja import Schema, NinjaAPI

from corpus.models import Annotation, Sentence, Document, User, Token
from corpus.views import user_profile

api = NinjaAPI()


class AnnotationSchema(Schema):
    sentence: int
    document: int
    user: int
    guid: str
    alt: str
    body: dict


class CorrectionsSchema(Schema):
    correction: str
    alt_correction: str


class UserSchema(Schema):
    id: str
    displayName: str


class ErrorSchema(Schema):
    errors: List[str]


class AnnotateRequest(Schema):
    original_sentence: str
    corrected_sentence: str


class AnnotationResponse(Schema):
    guid: str
    body: dict


@api.post("/auto_annotate/", response={200: List[AnnotationResponse]})
def auto_annotate(request, annotate_data: AnnotateRequest):
    original = annotate_data.original_sentence
    corrected = annotate_data.corrected_sentence

    edits, orig_tokenized, cor_tokenized = _ANNOTATOR.annotate(original, corrected)
    annotations = []
    for index, edit in enumerate(edits):
        original_tokens = edit.o_toks
        if len(original_tokens) == 0:
            original_tokens = [orig_tokenized.tokens[edit.o_start - 1]]
            edit.o_str = original_tokens[0].text
            edit.c_str = f"{edit.o_str} {edit.c_str}"
        original_start = original_tokens[0].start
        original_end = original_tokens[-1].stop

        guid = uuid4()
        annotation = {
            "guid": f"#{guid}",
            "body": {
                "id": f"#{guid}",
                "body": [
                    {
                        "type": "TextualBody",
                        "value": edit.type,
                        "created": datetime.now().isoformat(),
                        "creator": {"id": "/corpus/user_profile/", "name": "auto"},
                        "purpose": "tagging",
                    },
                    {
                        "type": "TextualBody",
                        "value": edit.c_str,
                        "created": datetime.now().isoformat(),
                        "creator": {"id": "/corpus/user_profile/", "name": "auto"},
                        "purpose": "commenting",
                    },
                ],
                "type": "Annotation",
                "target": {
                    "selector": [
                        {
                            "type": "TextQuoteSelector",
                            "exact": edit.o_str,
                        },
                        {
                            "type": "TextPositionSelector",
                            "start": original_start,
                            "end": original_end,
                        },
                    ]
                },
                "@context": "http://www.w3.org/ns/anno.jsonld",
            },
        }
        annotations.append(annotation)

    return annotations


@api.get("/annotations/get/{sentence_id}/", response=List[Dict])
def get_sentence_annotations(request, sentence_id: int):
    sentence_annotations = Annotation.objects.filter(sentence=sentence_id, alt=False)
    data = [annotation.json for annotation in sentence_annotations]
    return data


@api.get("/annotations/get/alt/{sentence_id}/", response=List[Dict])
def get_alt_sentence_annotations(request, sentence_id: int):
    sentence_annotations = Annotation.objects.filter(sentence=sentence_id, alt=True)
    data = [annotation.json for annotation in sentence_annotations]
    return data


@api.post("/annotations/create/")
def create_annotation(request, annotation_data: AnnotationSchema):
    annotation = Annotation.objects.create(
        sentence=Sentence.objects.get(id=annotation_data.sentence),
        document=Document.objects.get(id=annotation_data.document),
        user=User.objects.get(id=annotation_data.user),
        guid=annotation_data.guid,
        alt=True if annotation_data.alt == "true" else False,
        json=annotation_data.body,
    )

    return {"id": annotation.guid}


@api.put("/annotations/update/")
def update_annotation(request, annotation_data: AnnotationSchema):
    annotation = get_object_or_404(Annotation, guid=annotation_data.guid)
    annotation.json = annotation_data.body
    annotation.save()
    return {"id": annotation.guid}


@api.delete("/annotations/delete/")
def delete_annotation(request, annotation_data: AnnotationSchema):
    annotation = Annotation.objects.get(guid=annotation_data.guid)
    annotation.delete()
    return {"id": annotation.guid}


@api.get("/get_corrections/{sentence_id}/", response={200: CorrectionsSchema})
def get_sentence_corrections(request, sentence_id: int):
    sentence = Sentence.objects.get(id=sentence_id)
    data = {
        "correction": sentence.correction,
        "alt_correction": sentence.alt_correction,
    }
    return data


@api.get("/get_user_info/", response={200: UserSchema})
def get_user_info(request):
    user = User.objects.get(id=request.user.id)
    data = {
        "id": redirect(user_profile).url,
        "displayName": user.username,
    }
    return data


@api.get("/get_sentence_errors/{sentence_id}/", response={200: ErrorSchema})
def get_sentence_errors(request, sentence_id: int):
    sentence = Sentence.objects.get(id=sentence_id)
    words = Token.objects.filter(sentence=sentence).values_list("token", flat=True)
    errors = [word for word in words if not _DICTIONARY.check(word)]
    return {"errors": errors}
