import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.models import City, Governorate


class Command(BaseCommand):
    help = "Load Egypt's governorates/cities from static/data/egypt-governorates.json into the database"

    def handle(self, *args, **options):
        data_path = os.path.join(settings.BASE_DIR, "static", "data", "egypt-governorates.json")

        with open(data_path, encoding="utf-8") as f:
            governorates = json.load(f)

        # update_or_create keyed by the JSON's own id, so this is safe to
        # rerun (e.g. after editing the JSON) without duplicating rows or
        # disturbing any ShippingFee/Order/SellWithUsRequest rows that
        # already reference these ids.
        governorate_count = 0
        city_count = 0
        for gov_data in governorates:
            governorate, _ = Governorate.objects.update_or_create(
                id=gov_data["id"],
                defaults={"name_ar": gov_data["name_ar"], "name_en": gov_data["name_en"]},
            )
            governorate_count += 1

            for city_data in gov_data["cities"]:
                City.objects.update_or_create(
                    id=city_data["id"],
                    defaults={
                        "governorate": governorate,
                        "name_ar": city_data["name_ar"],
                        "name_en": city_data["name_en"],
                    },
                )
                city_count += 1

        self.stdout.write(self.style.SUCCESS(f"Loaded {governorate_count} governorates and {city_count} cities"))
