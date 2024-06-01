from django.core.management.base import BaseCommand
from django.apps import apps
import csv


class Command(BaseCommand):
    help = "Creating model objects according the file path specified"

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="file path")
        parser.add_argument("--model_name", type=str, help="model name")
        parser.add_argument("--app_name", type=str, help="django app name that the model is connected to")

    def handle(self, *args, **options):
        file_path = options["path"]
        app_name = options["app_name"]
        model_name = options["model_name"]
        _model = apps.get_model(f"{app_name}.{model_name}")

        with open(file_path, "r") as csv_file:
            reader = csv.reader(csv_file, delimiter=",", quotechar="|")
            header = next(reader)
            print(header)
            for row in reader:
                try:
                    _object_dict = {key: value for key, value in zip(header, row)}
                    _model.objects.create(**_object_dict)
                except Exception as e:
                    print(e, _object_dict)

            self.stdout.write(self.style.SUCCESS("Data processed successfully"))
