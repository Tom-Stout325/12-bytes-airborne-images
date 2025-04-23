import csv
import os
from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from your_app.models import (
    Type, Category, SubCategory, Keyword, Team, Client, Service,
    Transaction, Invoice, InvoiceItem, MileageRate, Miles
)

class Command(BaseCommand):
    help = 'Import data from CSV files into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_dir', type=str, help='Directory containing CSV files')

    def handle(self, *args, **kwargs):
        csv_dir = kwargs['csv_dir']
        self.stdout.write(self.style.SUCCESS(f'Processing CSV files in {csv_dir}'))

        # Define the order of models to process (to respect ForeignKey dependencies)
        model_files = [
            ('types.csv', Type, ['trans_type']),
            ('categories.csv', Category, ['category']),
            ('subcategories.csv', SubCategory, ['sub_cat']),
            ('keywords.csv', Keyword, ['name']),
            ('teams.csv', Team, ['name']),
            ('clients.csv', Client, ['business', 'first', 'last', 'street', 'address2', 'email', 'phone']),
            ('services.csv', Service, ['service']),
            ('mileage_rates.csv', MileageRate, ['rate']),
            ('invoices.csv', Invoice, ['invoice_numb', 'client', 'event', 'location', 'keyword', 'service', 'amount', 'date', 'due', 'paid']),
            ('invoice_items.csv', InvoiceItem, ['invoice', 'item', 'qty', 'price']),
            ('miles.csv', Miles, ['date', 'begin', 'end', 'client', 'invoice', 'tax', 'job', 'vehicle', 'mileage_type']),
            ('transactions.csv', Transaction, ['date', 'trans_type', 'category', 'sub_cat', 'amount', 'invoice_numb', 'paid', 'team', 'transaction', 'tax', 'keyword', 'receipt']),
        ]

        for csv_file, model, fields in model_files:
            file_path = os.path.join(csv_dir, csv_file)
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f'{csv_file} not found, skipping...'))
                continue

            self.stdout.write(f'Processing {csv_file} for {model.__name__}')
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        self.import_row(model, row, fields)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error processing row {row}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Import completed'))

    def import_row(self, model, row, fields):
        # Prepare data dictionary
        data = {}
        for field in fields:
            value = row.get(field)
            if value == '' or value is None:
                data[field] = None
            else:
                # Handle ForeignKey fields
                if field in ['trans_type', 'category', 'sub_cat', 'team', 'keyword', 'client', 'service', 'item', 'invoice']:
                    data[field] = self.get_foreign_key(field, value)
                elif field == 'date' or field == 'due':
                    data[field] = datetime.strptime(value, '%Y-%m-%d').date()
                elif field in ['amount', 'price', 'rate', 'begin', 'end', 'total']:
                    data[field] = Decimal(value)
                elif field == 'qty':
                    data[field] = int(value)
                else:
                    data[field] = value

        # Handle special cases
        if model == Transaction and 'receipt' in row and row['receipt']:
            # Assuming receipt files are accessible in the filesystem
            receipt_path = row['receipt']
            if os.path.exists(receipt_path):
                with open(receipt_path, 'rb') as f:
                    data['receipt'] = File(f, name=os.path.basename(receipt_path))

        if model == Miles:
            # Total is calculated automatically in the model's save method
            data.pop('total', None)

        # Create or update the record
        if model == Invoice:
            # Use invoice_numb as unique identifier
            instance, created = model.objects.get_or_create(invoice_numb=data['invoice_numb'], defaults=data)
        elif model == Client:
            # Use email as unique identifier
            instance, created = model.objects.get_or_create(email=data['email'], defaults=data)
        else:
            instance = model(**data)
            instance.save()

    def get_foreign_key(self, field, value):
        field_to_model = {
            'trans_type': Type,
            'category': Category,
            'sub_cat': SubCategory,
            'team': Team,
            'keyword': Keyword,
            'client': Client,
            'service': Service,
            'item': Service,
            'invoice': Invoice,
        }
        model = field_to_model[field]
        if model == Client:
            return model.objects.get(business=value)
        elif model == Invoice:
            return model.objects.get(invoice_numb=value)
        else:
            return model.objects.get(**{model._meta.model.__str__.__name__.lower(): value})