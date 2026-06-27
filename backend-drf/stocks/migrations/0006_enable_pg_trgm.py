from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0005_trainingrun"),
    ]

    operations = [
        # Enables similarity()/% operators used for fuzzy stock search.
        TrigramExtension(),
    ]
