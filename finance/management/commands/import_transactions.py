import csv
import datetime
from django.core.management.base import BaseCommand
from finance.models import Transaction, Type, Category, SubCategory, Team, Keyword
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Import transactions from CSV"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        user = User.objects.first()  # Adjust to your user logic

        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames and '\ufeffdate' in reader.fieldnames:
                reader.fieldnames = [field.lstrip('\ufeff') for field in reader.fieldnames]
            for row in reader:
                try:
                    trans_type, _ = Type.objects.get_or_create(name=row['Transaction Type'])
                    category, _ = Category.objects.get_or_create(name=row['CATEGORY'])
                    sub_cat, _ = SubCategory.objects.get_or_create(name=row['SUB-CATEGORY'])
                    team, _ = Team.objects.get_or_create(name=row['Team']) if row['Team'] else (None, False)
                    keyword, _ = Keyword.objects.get_or_create(name=row['Keyword']) if row['Keyword'] else (Keyword.objects.get(pk=1), False)

                    transaction = Transaction(
                        date=datetime.datetime.strptime(row['Transaction Date'], '%m/%d/%y').date(),
                        date_created=datetime.datetime.strptime(row['Date Created'], '%m/%d/%y').date(),
                        trans_type=trans_type,
                        category=category,
                        sub_cat=sub_cat,
                        amount=row['AMOUNT'],
                        invoice_numb=row['Invoice Number'],
                        paid=row['Paid'] or "No",
                        team=team,
                        transaction=row['Transaction'],
                        tax=row['Tax'] or "Yes",
                        keyword=keyword,
                        user=user,
                    )
                    transaction.save()
                    self.stdout.write(self.style.SUCCESS(f"Imported: {transaction.transaction}"))
                except Exception as e:
                    self.stderr.write(f"Error importing row: {row}\n{e}")
