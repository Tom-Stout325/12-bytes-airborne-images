from django.core.management.base import BaseCommand
from django.core import management
from django.core.mail import send_mail
import datetime
import os
import glob
import boto3
from django.conf import settings

class Command(BaseCommand):
    help = "Creates a JSON backup of the entire database, uploads to S3, and sends email notification with recent backups listed."

    def handle(self, *args, **kwargs):
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)

        filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        local_path = os.path.join(backup_dir, filename)

        try:
            # ✅ Create local backup
            with open(local_path, "w") as f:
                management.call_command("dumpdata", indent=2, stdout=f)
            self.stdout.write(self.style.SUCCESS(f"✅ Local backup created: {local_path}"))

            # ✅ Upload to S3 (if enabled)
            s3_message = "S3 upload skipped"
            s3_recent_list = []
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
                s3_message = f"✅ Uploaded to S3: s3://{bucket}/{s3_key}"
                self.stdout.write(self.style.SUCCESS(s3_message))

                # ✅ Keep only 2 most recent backups on S3
                backups = s3.list_objects_v2(Bucket=bucket, Prefix="backups/").get("Contents", [])
                sorted_backups = sorted(backups, key=lambda x: x["LastModified"], reverse=True)

                if len(sorted_backups) > 2:
                    for old in sorted_backups[2:]:
                        s3.delete_object(Bucket=bucket, Key=old["Key"])
                        self.stdout.write(self.style.WARNING(f"🗑️ Deleted old S3 backup: {old['Key']}"))

                # ✅ Collect the 2 most recent S3 backups for email reference
                s3_recent_list = [f"{b['Key']} ({b['LastModified']})" for b in sorted_backups[:2]]

            # ✅ Get 2 most recent local backups for email reference
            local_backups = sorted(glob.glob(f"{backup_dir}/backup_*.json"), reverse=True)[:2]

            # ✅ Format the email message
            message = (
                f"The database backup completed successfully.\n\n"
                f"Local Backup Created:\n  {local_path}\n"
                f"{s3_message}\n\n"
                f"📂 Recent Local Backups:\n  " + "\n  ".join(local_backups) + "\n\n"
                f"☁️ Recent S3 Backups:\n  " + ("\n  ".join(s3_recent_list) if s3_recent_list else "No S3 backups found") + "\n\n"
                f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            self.send_email(subject="✅ Database Backup Successful", message=message)

        except Exception as e:
            error_message = f"❌ Backup failed: {e}"
            self.stdout.write(self.style.ERROR(error_message))

            self.send_email(
                subject="❌ Database Backup Failed",
                message=f"The database backup failed.\n\nError:\n{e}\n\n"
                        f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

    def send_email(self, subject, message):
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
