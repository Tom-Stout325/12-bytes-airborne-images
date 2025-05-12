from django.core.management.base import BaseCommand
from finance.models import RecurringTransaction, Transaction
from django.utils.timezone import now
from datetime import date
from calendar import monthrange

class Command(BaseCommand):
    help = 'Generate recurring transactions for a specific month and year (defaults to current month).'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, help='Year to generate transactions for')
        parser.add_argument('--month', type=int, help='Month to generate transactions for')

    def handle(self, *args, **kwargs):
        today = now().date()
        year = kwargs.get('year') or today.year
        month = kwargs.get('month') or today.month

        last_day = monthrange(year, month)[1]
        created = 0
        skipped = 0

        recurrences = RecurringTransaction.objects.filter(active=True)

        for r in recurrences:
            target_day = min(r.day, last_day)
            trans_date = date(year, month, target_day)

            exists = Transaction.objects.filter(
                user=r.user,
                transaction=r.transaction,
                date=trans_date
            ).exists()

            if exists:
                skipped += 1
                continue

            Transaction.objects.create(
                date=trans_date,
                trans_type=r.trans_type,
                category=r.category,
                sub_cat=r.sub_cat,
                amount=r.amount,
                transaction=r.transaction,
                team=r.team,
                keyword=r.keyword,
                tax=r.tax,
                user=r.user,
                paid="Yes"
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"{created} transactions created for {year}-{month:02d}. {skipped} skipped."
        ))
