from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
import os

class Command(BaseCommand):
    help = 'Backup the database to a JSON file'

    def handle(self, *args, **options):
        # Create backups directory if it doesn't exist
        backup_dir = os.path.join(os.getcwd(), 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Generate filename with timestamp
        timestamp = timezone.now().strftime('%Y-%m-%d_%H%M%S')
        filename = f'backup_{timestamp}.json'
        filepath = os.path.join(backup_dir, filename)

        self.stdout.write(f'Starting backup to {filepath}...')

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                call_command('dumpdata', indent=2, stdout=f)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully backed up database to {filepath}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Backup failed: {str(e)}'))
