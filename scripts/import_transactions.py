import csv
from datetime import datetime
from decimal import Decimal
from django.contrib.auth import get_user_model
from finance.models import Invoice, Client, Keyword, Service

CSV_FILE_PATH = "data/invoice.csv"

User = get_user_model()
user = User.objects.get(username='tomstout')

created_count = 0
skipped_count = 0

with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            invoice_numb = row['invoice_numb'].strip()
            if Invoice.objects.filter(invoice_numb=invoice_numb).exists():
                skipped_count += 1
                continue

            date = datetime.strptime(row['date'], '%m/%d/%y')
            due = datetime.strptime(row['due'], '%m/%d/%y')
            paid_date = None
            if row['paid_date'].strip():
                try:
                    paid_date = datetime.strptime(row['paid_date'].strip(), '%m/%d/%y')
                except Exception:
                    print(f"⚠️ Invalid paid_date format: {row['paid_date']}")

            # Client
            client_name = row['client_id'].strip()
            client, _ = Client.objects.get_or_create(business__iexact=client_name, defaults={'business': client_name, 'email': 'unknown@example.com'})

            # Keyword
            keyword_name = row['keyword_id'].strip()
            keyword, _ = Keyword.objects.get_or_create(name__iexact=keyword_name, defaults={'name': keyword_name})

            # Service (assume Drone Services already exists)
            service_name = row['service_id'].strip()
            try:
                service = Service.objects.get(service__iexact=service_name)
            except Service.DoesNotExist:
                service = Service.objects.create(service=service_name)

            amount = Decimal(row['amount'])
            status = row.get('status', 'Unpaid')

            invoice = Invoice(
                invoice_numb=invoice_numb,
                client=client,
                event=row.get('event', '').strip(),
                location=row.get('location', '').strip(),
                keyword=keyword,
                service=service,
                amount=amount,
                date=date,
                due=due,
                paid_date=paid_date,
                status=status
            )
            invoice.save()
            created_count += 1

        except Exception as e:
            print(f"❌ Error importing row: {row}")
            print(f"   → {e}")

print(f"✅ Successfully imported {created_count} invoices.")
print(f"➖ Skipped {skipped_count} duplicate invoices.")
