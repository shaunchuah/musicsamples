from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from app.factories import SampleFactory
from app.models import Sample

NUM_SAMPLES = 358


class Command(BaseCommand):
    help = "Generates dummy data. **WARNING: This is only for running in development. "
    "Running this in production will lead to irreversible data loss."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        if settings.DEBUG:
            self.stdout.write("Deleting old data...")
            models = [Sample]
            for m in models:
                m.objects.all().delete()

            self.stdout.write("Creating new data...")

            # Add some users to workspaces
            for _ in range(NUM_SAMPLES):
                SampleFactory()

            self.stdout.write(f"Successfully added {NUM_SAMPLES} samples.")
        else:
            self.stderr.write(
                "WARNING: You are not allowed to run this command in production. "
                "This will delete all production data. Only if DEBUG=True"
            )
