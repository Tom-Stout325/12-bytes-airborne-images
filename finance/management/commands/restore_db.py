from django.core.management.base import BaseCommand
from django.core import management
from django.core.mail import send_mail
import boto3
import tempfile
import os
import glob
import datetime
from django.conf import settings

class Command(BaseCommand):
    help = "Restores the database from a JSON backup (supports S3 or local file) and sends email notification."

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

        try:
            if use_s3:
                self.restore_from_s3(filename)
            else:
                self.restore_from_local(filename)

            # ✅ Email notification on success
            self.send_restore_email(success=True, filename=filename, from_s3=use_s3)

        except Exception as e:
            error_message = f"❌ Restore failed: {e}"
            self.stdout.write(self.style.ERROR(error_message))

            # ✅ Email notification on failure
            self.send_restore_email(success=False, filename=filename, from_s3=use_s3, error=e)

    def restore_from_local(self, filename):
        management.call_command("loaddata", filename)
        self.stdout.write(self.style.SUCCESS(f"✅ Database restored from local file: {filename}"))

    def restore_from_s3(self, filename):
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        s3_key = filename if filename.startswith("backups/") else f"backups/{filename}"

        # ✅ Download to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
            s3.download_file(bucket, s3_key, tmp_file.name)
            tmp_file.flush()
            management.call_command("loaddata", tmp_file.name)
            self.stdout.write(self.style.SUCCESS(f"✅ Database restored from S3: s3://{bucket}/{s3_key}"))

        os.remove(tmp_file.name)

    def send_restore_email(self, success=True, filename=None, from_s3=False, error=None):
        """Send email notification after restore attempt."""

        # ✅ Get 2 most recent local backups
        backup_dir = "backups"
        local_backups = sorted(glob.glob(f"{backup_dir}/backup_*.json"), reverse=True)[:2]

        # ✅ Get 2 most recent S3 backups
        s3_recent_list = []
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
                sorted_backups = sorted(backups, key=lambda x: x["LastModified"], reverse=True)
                s3_recent_list = [f"{b['Key']} ({b['LastModified']})" for b in sorted_backups[:2]]
            except Exception as e:
                s3_recent_list = [f"⚠️ Error fetching S3 backups: {e}"]

        # ✅ Format email
        if success:
            subject = "✅ Database Restore Successful"
            message = (
                f"The database was restored successfully.\n\n"
                f"Restored From: {'S3' if from_s3 else 'Local'}\n"
                f"Backup File: {filename}\n\n"
                f"📂 Recent Local Backups:\n  " + "\n  ".join(local_backups) + "\n\n"
                f"☁️ Recent S3 Backups:\n  " + ("\n  ".join(s3_recent_list) if s3_recent_list else "No S3 backups found") + "\n\n"
                f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        else:
            subject = "❌ Database Restore Failed"
            message = (
                f"The database restore failed.\n\n"
                f"Restored From: {'S3' if from_s3 else 'Local'}\n"
                f"Backup File: {filename}\n"
                f"Error:\n{error}\n\n"
                f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS("📧 Email notification sent."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to send email: {e}"))




# Restore From Local
# python manage.py restore_db backups/backup_20250716_170501.json
#
# Restore from S3:
# python manage.py restore_db backup_20250716_170501.json --s3
