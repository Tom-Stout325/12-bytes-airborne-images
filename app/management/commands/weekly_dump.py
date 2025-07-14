import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils.timezone import now
from pathlib import Path

class Command(BaseCommand):
    help = 'Dumps the database to a JSON file every week.'

    def handle(self, *args, **options):
        today = now().strftime('%Y-%m-%d')
        backup_dir = Path(__file__).resolve().parent.parent.parent.parent / 'backups'
        backup_dir.mkdir(exist_ok=True)

        file_path = backup_dir / f'dump_{today}.json'
        with open(file_path, 'w') as f:
            call_command('dumpdata', '--natural-primary', '--natural-foreign', '--indent', '2', stdout=f)
        
        self.stdout.write(self.style.SUCCESS(f'Database backup saved to {file_path}'))
