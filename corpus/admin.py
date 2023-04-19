from django.contrib import admin

from corpus.models import Document, Annotation, Author

admin.site.register(Document)
admin.site.register(Annotation)
admin.site.register(Author)
