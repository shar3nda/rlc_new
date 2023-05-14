import datetime
import json
import uuid

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect

from auto_annotator.annotator import Annotator
from corpus.models import Annotation, Document, Sentence
from corpus.views import user_profile


def get_word_positions(sentence, words, word_number):
    if word_number > len(words) or word_number < 1:
        raise ValueError(
            f"Word number is out of range (len={len(words)}, number={word_number})"
        )

    target_word = words[word_number - 1]
    start_position = sentence.find(target_word)

    if start_position == -1:
        raise ValueError(f"Word '{target_word}' not found in sentence '{sentence}'")

    end_position = start_position + len(target_word) - 1
    return start_position, end_position


@permission_required("corpus.add_annotation", raise_exception=True)
def auto_annotate(request):
    """
    This API endpoint automatically generates annotations for a corrected sentence.

    Method: POST
    URL: /api/auto_annotate/

    Request Body:
    {
        "original_sentence": <original_sentence>,
        "corrected_sentence": <corrected_sentence>
    }

    Response:
    {
        "annotations": [
            <annotation 1 in W3C format>,
            <annotation 2 in W3C format>,
            ...
        ]
    }

    This endpoint accepts an original and a corrected sentence. It then applies
    automatic annotation logic to the sentences, generating a list of annotations
    that represent the differences between the original and corrected sentences.
    Each annotation includes information about the type of edit, the corrected
    text, and the position of the original text within the original sentence.

    If the request method is not POST, an error message is returned.
    """
    if request.method == "POST":
        original = request.POST["original_sentence"]
        corrected = request.POST["corrected_sentence"]
    else:
        return JsonResponse({"error": "Only POST requests are allowed."})

    a = Annotator()
    edits, orig_tokenized, cor_tokenized = a.annotate(original, corrected)
    annotations = []
    for index, edit in enumerate(edits):
        original_tokens = edit.o_toks
        if len(original_tokens) == 0:
            text, tokens, number = (
                original,
                [tok.text for tok in orig_tokenized.tokens],
                edit.o_start,
            )
            original_start, original_end = get_word_positions(text, tokens, number)
        else:
            original_start = original_tokens[0].start
            original_end = original_tokens[-1].stop

        guid = uuid.uuid4()
        annotation = {
            "guid": f"#{guid}",
            "body": {
                "id": f"#{guid}",
                "body": [
                    {
                        "type": "TextualBody",
                        "value": edit.type,
                        "created": datetime.datetime.now().isoformat(),
                        "creator": {"id": "/corpus/user_profile/", "name": "auto"},
                        "purpose": "tagging",
                    },
                    {
                        "type": "TextualBody",
                        "value": edit.c_str,
                        "created": datetime.datetime.now().isoformat(),
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

    return JsonResponse({"annotations": annotations})


def get_sentence_annotations(request, sentence_id):
    """
    This API endpoint returns all annotations for a specific sentence.

    Method: GET
    URL: /api/sentence_annotations/{sentence_id}/

    Response: [{annotation1}, {annotation2}, ...]
    """
    if request.method == "GET":
        sentence_annotations = Annotation.objects.filter(
            sentence=sentence_id, alt=False
        )
        data = [annotation.json for annotation in sentence_annotations]
        return JsonResponse(data, safe=False)


def get_alt_sentence_annotations(request, sentence_id):
    """
    This API endpoint returns all alternate annotations for a specific sentence.

    Method: GET
    URL: /api/alt_sentence_annotations/{sentence_id}/

    Response: [{annotation1}, {annotation2}, ...]
    """
    if request.method == "GET":
        sentence_annotations = Annotation.objects.filter(sentence=sentence_id, alt=True)
        data = [annotation.json for annotation in sentence_annotations]
        return JsonResponse(data, safe=False)


@permission_required("corpus.add_annotation", raise_exception=True)
def create_annotation(request):
    """
    This API endpoint creates a new annotation.

    Method: POST
    URL: /api/annotation/

    Request Body:
    {
        "sentence": <sentence_id>,
        "document": <document_id>,
        "user": <user_id>,
        "guid": <guid>,
        "alt": <true_or_false>,
        "body": <json_data>,
    }

    Response:
    {
        "id": <annotation_id>
    }
    """
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


@permission_required("corpus.change_annotation", raise_exception=True)
def update_annotation(request):
    """
    This API endpoint updates an existing annotation.

    Method: PUT
    URL: /api/annotation/

    Request Body:
    {
        "guid": <guid>,
        "body": <json_data>,
    }

    Response:
    {
        "id": <annotation_id>
    }
    """
    if request.method == "PUT":
        data = json.loads(request.body)
        annotation_id = json.loads(request.body)["guid"]
        annotation = Annotation.objects.get(guid=annotation_id)
        annotation.json = data["body"]
        annotation.save()
        return JsonResponse({"id": annotation.id})


@permission_required("corpus.delete_annotation", raise_exception=True)
def delete_annotation(request):
    """
    This API endpoint deletes an existing annotation.

    Method: DELETE
    URL: /api/annotation/

    Request Body:
    {
        "guid": <guid>
    }

    Response:
    {
        "id": <annotation_id>
    }
    """
    if request.method == "DELETE":
        annotation_id = json.loads(request.body)["guid"]
        annotation = Annotation.objects.get(guid=annotation_id)
        annotation.delete()
        return JsonResponse({"id": annotation_id})


def get_sentence_corrections(request, sentence_id):
    """
    This API endpoint returns the correction and alternative correction for a specific sentence.

    Method: GET
    URL: /api/sentence_corrections/{sentence_id}/

    Response:
    {
        "correction": <correction>,
        "alt_correction": <alt_correction>
    }
    """
    if request.method == "GET":
        sentence = Sentence.objects.get(id=sentence_id)
        data = {
            "correction": sentence.correction,
            "alt_correction": sentence.alt_correction,
        }
        return JsonResponse(data)


def get_user_info(request):
    """
    This API endpoint returns the user's profile and display name.

    Method: GET
    URL: /api/user_info/

    Response:
    {
        "id": <profile_url>,
        "displayName": <username>
    }
    """
    if request.method == "GET":
        user = User.objects.get(id=request.user.id)
        data = {
            "id": redirect(user_profile).url,
            "displayName": user.username,
        }
        return JsonResponse(data)
