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

            # Fix BOM issue
            if reader.fieldnames and '\ufeffdate' in reader.fieldnames:
                reader.fieldnames = [field.lstrip('\ufeff') for field in reader.fieldnames]

            for row in reader:
                try:
                    trans_type, _ = Type.objects.get_or_create(name=row['trans_type'])
                    category, _ = Category.objects.get_or_create(name=row['category'])
                    sub_cat, _ = SubCategory.objects.get_or_create(name=row['sub_cat'])
                    team = None
                    if row['team']:
                        team, _ = Team.objects.get_or_create(name=row['team'])

                    # Handle missing or fallback keyword
                    keyword = Keyword.objects.get_or_create(name=row['keyword'])[0] if row['keyword'] else Keyword.objects.get(pk=1)

                    # Resolve user from username
                    user = User.objects.get(username=row['user'])

                    # Handle receipt field — just save as string placeholder (optional)
                    receipt = None
                    if row['receipt'] and row['receipt'].lower() != 'na':
                        receipt = row['receipt']  # This does not upload a file, just stores the path/label

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
                        receipt=receipt
                    )
                    transaction.save()
                    self.stdout.write(self.style.SUCCESS(f"Imported: {transaction.transaction}"))
                except Exception as e:
                    self.stderr.write(f"Error importing row: {row}\n{e}")
