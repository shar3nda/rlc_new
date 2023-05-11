import json
import os
import random

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rlc_new.settings")
django.setup()
from django.contrib.auth.models import User
from tqdm import tqdm

from corpus.models import Document, Author

users = User.objects.all()
authors = Author.objects.all()
num_documents = 50

# load docs from backup/annotator_document.json
with open("../backup/annotator_document.json", "r") as f:
    docs = json.load(f)
    # delete documents with body "loaded from xml"
    docs = [doc for doc in docs if doc["body"] != "loaded from xml"]

for doc in tqdm(docs, desc="Creating documents"):
    if doc["body"] == "loaded from xml":
        continue
    Document.objects.create(
        title=doc["title"],
        user=random.choice(users),
        author=Author.objects.create(
            name=doc["author"],
            gender=doc["gender"],
            language_background=doc["language_background"],
        ),
        date=random.choice([2022, 2023]),
        genre=doc["genre"],
        subcorpus=doc["subcorpus"],
        language_level=doc["level"],
        status=2 if doc["checked"] else (1 if doc["annotated"] else 0),
        body=doc["body"],
    )
