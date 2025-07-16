from django.core.management.base import BaseCommand
import os
import boto3
from django.conf import settings

class Command(BaseCommand):
    help = "Lists available database backups (local and S3)"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("📂 Checking available backups...\n"))

        # ✅ List local backups
        backup_dir = "backups"
        if os.path.exists(backup_dir):
            local_backups = sorted(os.listdir(backup_dir), reverse=True)
            if local_backups:
                self.stdout.write(self.style.SUCCESS("✅ Local Backups:"))
                for f in local_backups:
                    self.stdout.write(f"   - {f}")
            else:
                self.stdout.write(self.style.WARNING("⚠️ No local backups found."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ No local backups folder found."))

        # ✅ List S3 backups (if enabled)
        if getattr(settings, "USE_S3", False):
            try:
                s3 = boto3.client(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME,
                )
                bucket = settings.AWS_STORAGE_BUCKET_NAME
                backups = s3.list_objects_v2(Bucket=bucket, Prefix="backups/").get("Contents", [])
                backups = sorted(backups, key=lambda x: x["LastModified"], reverse=True)

                if backups:
                    self.stdout.write("\n✅ S3 Backups:")
                    for b in backups:
                        self.stdout.write(f"   - {b['Key']} ({b['LastModified']})")
                else:
                    self.stdout.write(self.style.WARNING("\n⚠️ No S3 backups found."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error listing S3 backups: {e}"))



# Local Run Command:
# python manage.py list_backups
