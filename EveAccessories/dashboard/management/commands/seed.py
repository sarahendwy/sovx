from django.core.management.base import BaseCommand

from dashboard.models import Setting


class Command(BaseCommand):
    help = "Seed the database with sample data for local development"

    def handle(self, *args, **options):
        self.seed_settings()

    def seed_settings(self):
        setting = Setting.objects.first()
        offer_banner_text = "اطلب قبل 18 ديسمبر علشان توصلك الأوردرات قبل الكريسماس 🎄🎁"

        if setting is None:
            setting = Setting.objects.create(offer_banner_text=offer_banner_text)
            self.stdout.write(self.style.SUCCESS("Created site settings"))
        else:
            setting.offer_banner_text = offer_banner_text
            setting.save()
            self.stdout.write(self.style.SUCCESS("Updated site settings"))
