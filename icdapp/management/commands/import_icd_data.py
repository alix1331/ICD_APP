from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import pandas as pd

COLUMNS = [
    "category_code",
    "diagnosis_code",
    "full_code",
    "abbreviated_description",
    "full_description",
    "category_title",
]


class Command(BaseCommand):
    help = """Import ICD CSV into Django Models

    usage:
        python manage.py import_icd_data --path icd_codes.csv            (only if the table is empty)
        python manage.py import_icd_data --path icd_codes.csv --replace  (delete existing rows first)
        python manage.py import_icd_data --path icd_codes.csv --append   (add on top of existing rows)
    """

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="CSV file path", default="icd_codes.csv")
        parser.add_argument("--batch-size", type=int, default=5000, help="rows per INSERT batch")
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument("--replace", action="store_true", help="delete all existing rows before importing")
        mode.add_argument("--append", action="store_true", help="import even if the table already has rows")

    def handle(self, *args, **options):
        file_path = options["path"]
        batch_size = options["batch_size"]
        model = apps.get_model("icdapp", "ICDModel")

        existing = model.objects.count()
        if existing and not (options["replace"] or options["append"]):
            raise CommandError(
                f"The table already contains {existing} rows. Re-running the import would duplicate them. "
                "Use --replace to start over or --append to add anyway."
            )

        try:
            # dtype=str + keep_default_na=False: empty cells arrive as "" (not NaN) and
            # codes such as "NA" or "0010" are kept exactly as written.
            chunks = pd.read_csv(
                file_path,
                dtype=str,
                keep_default_na=False,
                usecols=lambda column: column in COLUMNS,  # skips the unnamed index column
                chunksize=20000,
            )

            total = 0
            with transaction.atomic():
                if options["replace"]:
                    model.objects.all().delete()
                for chunk in chunks:
                    missing = [c for c in COLUMNS if c not in chunk.columns]
                    if missing:
                        raise CommandError(f"CSV is missing column(s): {', '.join(missing)}")
                    instances = [
                        model(**{col: (record[col].strip() or None) for col in COLUMNS})
                        for record in chunk.to_dict("records")
                    ]
                    model.objects.bulk_create(instances, batch_size=batch_size)
                    total += len(instances)
        except FileNotFoundError:
            raise CommandError(f"File not found: {file_path}")

        self.stdout.write(self.style.SUCCESS(f"Finished importing {total} rows."))
