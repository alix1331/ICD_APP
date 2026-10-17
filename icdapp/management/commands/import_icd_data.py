from django.core.management.base import BaseCommand
from django.apps import apps
import pandas as pd


class Command(BaseCommand):
    help = """ Import ICD CSV into Django Models 
       usage: 
       python manage.py import_icd_data --path icd_codes.csv
       """

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            help="file path",
            default="icd_codes.csv",
        )

    def handle(self, *args, **options):
        file_path = options["path"]
        _model = apps.get_model("icdapp", "ICDModel")
        df = pd.read_csv(file_path)
        df_records = df.to_dict("records")

        model_instances = [_model(
            category_code=record.get("category_code"),
            diagnosis_code=record.get("diagnosis_code"),
            full_code=record.get("full_code"),
            abbreviated_description=record.get("abbreviated_description"),
            full_description=record.get("full_description"),
            category_title=record.get("category_title"),
        ) for record in df_records
        ]
        _model.objects.bulk_create(model_instances)
        print("Finished Importing Data")
