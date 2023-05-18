from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Annotation, Sentence


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = ["sentence", "document", "user", "guid", "alt", "json"]


class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = ["id", "correction", "alt_correction"]


class UserSerializer(serializers.ModelSerializer):
    displayName = serializers.CharField(source="username")

    class Meta:
        model = User
        fields = ["id", "displayName"]
