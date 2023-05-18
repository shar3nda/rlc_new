import datetime
import uuid

from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from auto_annotator.annotator import Annotator
from corpus.models import Annotation, Sentence, User, Document
from corpus.serializers import AnnotationSerializer, SentenceSerializer, UserSerializer


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
            original_tokens = [orig_tokenized.tokens[edit.o_start - 1]]
            edit.o_str = original_tokens[0].text
            edit.c_str = f"{edit.o_str} {edit.c_str}"
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


class AnnotationListCreateViewSet(viewsets.ModelViewSet):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    def create(self, request, *args, **kwargs):
        data = request.data
        sentence = get_object_or_404(Sentence, id=data.get("sentence"))
        document = get_object_or_404(Document, id=data.get("document"))
        user = get_object_or_404(User, id=data.get("user"))
        guid = data.get("guid")
        alt = data.get("alt")
        body = data.get("body")

        if not (sentence and document and user and guid and alt is not None and body):
            raise ValidationError("Required fields are missing")

        alt_bool = alt.lower() == "true"  # converting to boolean

        annotation = Annotation.objects.create(
            sentence=sentence,
            document=document,
            user=user,
            guid=guid,
            alt=alt_bool,
            json=body,
        )
        return Response({"id": annotation.id}, status=status.HTTP_201_CREATED)

    def list(self, request, sentence_id=None, alt=None):
        alt_bool = alt.lower() == "true"  # converting to boolean
        queryset = Annotation.objects.filter(sentence=sentence_id, alt=alt_bool)
        if sentence_id is not None:
            # get list of json fields
            return JsonResponse([a.json for a in queryset], safe=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AnnotationRetrieveUpdateDestroyViewSet(viewsets.ModelViewSet):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    def get_object(self):
        queryset = self.get_queryset()
        filter_kwargs = {"guid": self.kwargs["guid"]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.json = request.data.get("body")
        instance.save()
        return Response({"id": instance.id})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"id": instance.guid})


class SentenceViewSet(viewsets.ModelViewSet):
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer

    def retrieve(self, request, pk=None):
        queryset = Sentence.objects.get(id=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request):
        queryset = User.objects.get(id=request.user.id)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = User.objects.get(id=request.user.id)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)
