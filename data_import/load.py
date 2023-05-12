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
subcorpuses = Document.SubcorpusChoices.values
lang_levels = Document.LanguageLevelChoices.values
statuses = Document.StatusChoices.values

# load docs from backup/annotator_document.json
with open("../backup/annotator_document.json", "r") as f:
    docs = json.load(f)
    # delete documents with body "loaded from xml"
    docs = [doc for doc in docs if doc["body"] != "loaded from xml"]

for doc in tqdm(docs, desc="Creating documents"):
    Document.objects.create(
        title=doc["title"],
        user=random.choice(users),
        author=random.choice(authors),
        date=random.choice([2022, 2023]),
        genre=doc["genre"],
        subcorpus=random.choice(subcorpuses),
        language_level=random.choice(lang_levels),
        status=random.choice(statuses),
        body=doc["body"],
    )
