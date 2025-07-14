from finance.models import Invoice, InvoiceItem

# Only find invoices missing items
invoices = Invoice.objects.filter(items__isnull=True)

for invoice in invoices:
    InvoiceItem.objects.create(
        invoice=invoice,
        description="Drone Services",  # ← matches your model
        qty=1,
        price=invoice.amount
    )
    print(f"✅ Restored item for Invoice #{invoice.invoice_numb} with amount ${invoice.amount}")
