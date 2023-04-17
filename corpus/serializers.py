from rest_framework import serializers

from .models import Document, Sentence, Annotation, Token


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = (
            "id",
            "title",
            "user",
            "created_on",
            "body",
            "status",
        )


class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = (
            "id",
            "document",
            "text",
            "number",
        )


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = (
            "id",
            "document",
            "sentence",
            "user",
            "json",
        )
