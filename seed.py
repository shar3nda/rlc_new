import os
import random

import django
from faker import Faker
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rlc_new.settings")
django.setup()

from django.contrib.auth.models import User
from corpus.models import Document, Author
from content.models import Article, Section

fake = Faker("ru_RU")

# Create the admin user
print("Creating admin user")
User.objects.create_superuser(
    username="admin", email="admin@example.com", password="VerySecureAdminPassword123!"
)

# Create some fake users
num_users = 5
for _ in tqdm(range(num_users), desc="Creating users"):
    User.objects.create_user(
        username=fake.user_name(), email=fake.email(), password="VerySecureUserPassword123!"
    )

users = User.objects.all()

# Create some fake articles
num_articles = 10
for _ in tqdm(range(num_articles), desc="Creating articles"):
    article = Article(
        owner=random.choice(users),
        date=fake.date_between(start_date="-1y", end_date="today"),
        text_rus=fake.text(),
        text_eng=fake.text(),
    )
    article.save()

# Create some fake sections
num_sections = 5
for i in tqdm(range(num_sections), desc="Creating sections"):
    section = Section(
        text_rus=fake.text(),
        text_eng=fake.text(),
        header_rus=fake.sentence(),
        header_eng=fake.sentence(),
        number=i + 1,
    )
    section.save()

# Create some fake authors
num_authors = 10

for _ in tqdm(range(num_authors), desc="Creating authors"):
    Author.objects.create(
        name=fake.name(),
        gender=random.choice(Author.GenderChoices.values),
        program=fake.word(),
        language_background=random.choice(Author.LanguageBackgroundChoices.values),
        dominant_language=random.choice(Author.DominantLanguageChoices.values),
        source=fake.word(),
        favorite=fake.boolean(),
    )

authors = Author.objects.all()

# Create some fake documents
num_documents = 50
for _ in tqdm(range(num_documents), desc="Creating documents"):
    Document.objects.create(
        title=fake.sentence(),
        user=random.choice(users),
        author=random.choice(authors),  # Add a random author
        date=random.choice([2022, 2023]),
        genre=random.choice(Document.GenreChoices.values),
        subcorpus=random.choice(Document.SubcorpusChoices.values),
        language_level=random.choice(Document.LanguageLevelChoices.values),
        status=random.choice(Document.StatusChoices.values),
        body=fake.text(),
    )
print("Seeder completed!")
