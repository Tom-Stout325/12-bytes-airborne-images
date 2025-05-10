from django.core.management.base import BaseCommand
from finance.models import Transaction


class Command(BaseCommand):
    help = 'Reassign transactions from one category or subcategory to another'

    def add_arguments(self, parser):
        parser.add_argument('--category-from', type=int, help='Original Category ID')
        parser.add_argument('--category-to', type=int, help='New Category ID')
        parser.add_argument('--subcat', type=int, help='Filter by SubCategory ID')

    def handle(self, *args, **options):
        category_from = options['category_from']
        category_to = options['category_to']
        subcat_id = options['subcat']

        queryset = Transaction.objects.all()

        if subcat_id:
            queryset = queryset.filter(sub_cat_id=subcat_id)

        if category_from:
            queryset = queryset.filter(category_id=category_from)

        if not category_to:
            self.stderr.write("You must provide --category-to to reassign.")
            return

        updated_count = queryset.update(category_id=category_to)

        self.stdout.write(self.style.SUCCESS(
            f"Successfully reassigned {updated_count} transactions to category {category_to}."
        ))
