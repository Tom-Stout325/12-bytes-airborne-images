import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from finance.models import Transaction, Keyword

# ✅ Mapping: Invoice Number → Keyword
invoice_keyword_mapping = {
    240042: "Richmond",
    240047: "Norwalk",
    230012: "Phoenix",
    230011: "Gainesville",
    230014: "Vegas I",
    230015: "Norwalk",
    230016: "Denver",
    230017: "Seattle",
    230018: "Sonoma",
    230019: "Brainerd",
    230020: "Indy",
    230021: "Reading",
    230023: "St Louis",
    240033: "Chicago",
    240059: "Pomona II",
}

updated = 0
created_keywords = 0

for invoice_numb, keyword_name in invoice_keyword_mapping.items():
    # ✅ Get or create the keyword instance
    keyword_obj, created = Keyword.objects.get_or_create(name=keyword_name)
    if created:
        created_keywords += 1
        print(f"✅ Created new keyword: {keyword_name}")

    # ✅ Update all transactions with this invoice number
    transactions = Transaction.objects.filter(invoice_numb=str(invoice_numb))
    for trans in transactions:
        if trans.keyword != keyword_obj:
            trans.keyword = keyword_obj
            trans.save()
            updated += 1
            print(f"🔄 Updated Invoice {invoice_numb}: '{trans.transaction}' → {keyword_name}")

print(f"\n🎉 Finished!")
print(f"✔ Updated {updated} transactions")
print(f"✔ Created {created_keywords} new keywords")


# python3 manage.py shell < data/invoice_mapping.py
