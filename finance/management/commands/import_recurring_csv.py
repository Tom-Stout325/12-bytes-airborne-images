import csv
from django.core.management.base import BaseCommand
from finance.models import RecurringTransaction, Type, Category, SubCategory, Keyword, Team, User

class Command(BaseCommand):
    help = 'Import recurring expenses from a CSV file using foreign key IDs'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        path = kwargs['csv_file']
        created = 0
        skipped = 0

        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)  # comma is default


            for row in reader:
                row = {k.strip(): v for k, v in row.items()}  # <- Normalize keys

                try:
                    # Convert all foreign key IDs to integers
                    user = User.objects.get(id=int(row['user'].strip()))
                    trans_type = Type.objects.get(id=int(row['trans_type'].strip()))
                    category = Category.objects.get(id=int(row['category'].strip()))
                    sub_cat = SubCategory.objects.get(id=int(row['sub_cat'].strip()))

                    keyword = None
                    if row.get('keyword'):
                        keyword = Keyword.objects.get(id=int(row['keyword'].strip()))

                    team = None
                    if row.get('team'):
                        team = Team.objects.get(id=int(row['team'].strip()))

                    # Create the RecurringTransaction
                    RecurringTransaction.objects.create(
                        user=user,
                        trans_type=trans_type,
                        category=category,
                        sub_cat=sub_cat,
                        amount=row['amount'],
                        transaction=row['transaction'],
                        day=int(row['date'].strip()),
                        team=team,
                        keyword=keyword,
                        tax=row.get('tax', 'Yes'),
                        active=True
                    )

                    created += 1

                except Exception as e:
                    self.stderr.write(f"Skipped row: {row.get('transaction', 'Unknown')} — {e}")
                    skipped += 1
