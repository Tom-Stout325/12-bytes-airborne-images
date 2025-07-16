from django.core.management.base import BaseCommand
from django.core import management
import datetime
import os
import glob
import boto3
from django.conf import settings

class Command(BaseCommand):
    help = "Creates a JSON backup of the entire database and uploads to S3 (keeps 2 most recent backups)"

    def handle(self, *args, **kwargs):
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)

        # ✅ Create the local backup
        filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        local_path = os.path.join(backup_dir, filename)

        with open(local_path, "w") as f:
            management.call_command("dumpdata", indent=2, stdout=f)

        self.stdout.write(self.style.SUCCESS(f"✅ Local backup created: {local_path}"))

        # ✅ Upload to S3
        if getattr(settings, "USE_S3", False):
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            bucket = settings.AWS_STORAGE_BUCKET_NAME
            s3_key = f"backups/{filename}"

            s3.upload_file(local_path, bucket, s3_key)
            self.stdout.write(self.style.SUCCESS(f"✅ Uploaded to S3: s3://{bucket}/{s3_key}"))

            # ✅ Keep only 2 most recent backups on S3
            backups = s3.list_objects_v2(Bucket=bucket, Prefix="backups/").get("Contents", [])
            sorted_backups = sorted(backups, key=lambda x: x["LastModified"], reverse=True)

            if len(sorted_backups) > 2:
                for old in sorted_backups[2:]:
                    s3.delete_object(Bucket=bucket, Key=old["Key"])
                    self.stdout.write(self.style.WARNING(f"🗑️ Deleted old S3 backup: {old['Key']}"))

        self.stdout.write(self.style.SUCCESS("✔ Backup rotation complete (2 most recent kept on S3)"))





#Local Run Command:
# python manage.py backup_db
