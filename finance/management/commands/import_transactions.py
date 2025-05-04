import csv
import datetime
from django.core.management.base import BaseCommand
from finance.models import Transaction, Type, Category, SubCategory, Team, Keyword
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Import transactions from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)

            # Strip BOM if present in first header
            if reader.fieldnames and '\ufeffdate' in reader.fieldnames:
                reader.fieldnames = [field.lstrip('\ufeff') for field in reader.fieldnames]

            for row in reader:
                try:
                    # Lookup or create related fields using correct model fields
                    trans_type, _ = Type.objects.get_or_create(trans_type=row['trans_type'])
                    category, _ = Category.objects.get_or_create(category=row['category'])
                    sub_cat, _ = SubCategory.objects.get_or_create(sub_cat=row['sub_cat'])

                    team = None
                    if row['team']:
                        team, _ = Team.objects.get_or_create(name=row['team'])  # Adjust field name if different

                    keyword = (
                        Keyword.objects.get_or_create(name=row['keyword'])[0]
                        if row['keyword'] and row['keyword'].lower() != 'none'
                        else Keyword.objects.get(pk=1)
                    )

                    user = User.objects.get(username=row['user'])

                    receipt = row['receipt'] if row['receipt'] and row['receipt'].lower() != 'na' else None

                    transaction = Transaction(
                        date=datetime.datetime.strptime(row['date'], '%m/%d/%y').date(),
                        date_created=datetime.datetime.strptime(row['date_created'], '%m/%d/%y').date(),
                        trans_type=trans_type,
                        category=category,
                        sub_cat=sub_cat,
                        amount=row['amount'],
                        invoice_numb=row['invoice_numb'],
                        paid=row['paid'] or "No",
                        team=team,
                        transaction=row['transaction'],
                        tax=row['tax'] or "Yes",
                        keyword=keyword,
                        user=user,
                        receipt=receipt  # Just sets the field; does not upload a file
                    )
                    transaction.save()
                    self.stdout.write(self.style.SUCCESS(f"Imported: {transaction.transaction}"))

                except Exception as e:
                    self.stderr.write(f"Error importing row: {row}\n{e}")
