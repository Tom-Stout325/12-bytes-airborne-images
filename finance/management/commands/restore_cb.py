from django.core.management.base import BaseCommand
from django.core import management
import boto3
import tempfile
import os
from django.conf import settings

class Command(BaseCommand):
    help = "Restores the database from a JSON backup (supports S3 or local file)"

    def add_arguments(self, parser):
        parser.add_argument(
            "filename",
            type=str,
            help="Backup filename (e.g., 'backups/backup_20250716_170501.json'). "
                 "If using S3, just provide the key after 'backups/'."
        )
        parser.add_argument(
            "--s3",
            action="store_true",
            help="Restore directly from S3 instead of a local file."
        )

    def handle(self, *args, **options):
        filename = options["filename"]
        use_s3 = options["s3"]

        if use_s3:
            self.restore_from_s3(filename)
        else:
            self.restore_from_local(filename)

    def restore_from_local(self, filename):
        try:
            management.call_command("loaddata", filename)
            self.stdout.write(self.style.SUCCESS(f"✅ Database restored from local file: {filename}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error restoring database: {e}"))

    def restore_from_s3(self, filename):
        try:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            bucket = settings.AWS_STORAGE_BUCKET_NAME

            # Download to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
                s3_key = filename if filename.startswith("backups/") else f"backups/{filename}"
                s3.download_file(bucket, s3_key, tmp_file.name)
                tmp_file.flush()

                management.call_command("loaddata", tmp_file.name)
                self.stdout.write(self.style.SUCCESS(f"✅ Database restored from S3: s3://{bucket}/{s3_key}"))

            # Clean up temporary file
            os.remove(tmp_file.name)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error restoring from S3: {e}"))



#Restore Command:
# python manage.py restore_db backups/backup_20250716_170501.json
