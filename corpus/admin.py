from django.contrib import admin

from corpus.models import Document, Annotation

admin.site.register(Document)
admin.site.register(Annotation)
