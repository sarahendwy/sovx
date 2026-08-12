import os

from django.contrib.staticfiles.management.commands.runserver import (
    Command as StaticfilesRunserverCommand,
)
from django.core.management import call_command


class Command(StaticfilesRunserverCommand):
    def handle(self, *args, **options):
        # With the autoreloader on, handle() runs once in the watcher parent
        # process (RUN_MAIN unset) and once in the actual serving child
        # process (RUN_MAIN=true) - only seed in the process that serves.
        if not options.get("use_reloader") or os.environ.get("RUN_MAIN") == "true":
            call_command("seed")
        super().handle(*args, **options)
