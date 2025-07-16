import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from finance.models import Transaction, Keyword

keyword_mapping = {
    "san francisco": "Sonoma",
    "denver": "Denver",
    "gainesville": "Gainesville",
    "phoenix": "Phoenix",
    "affirm": "Monthly",
    "virginia": "Richmond",
}

updated = 0
created_keywords = 0

for trans in Transaction.objects.all():
    trans_name = trans.transaction.lower().strip()

    for word, keyword_name in keyword_mapping.items():
        if word in trans_name:
            # ✅ Get or create Keyword instance (must be Keyword instance, not string)
            keyword_obj, created = Keyword.objects.get_or_create(name=keyword_name)

            if created:
                created_keywords += 1
                print(f"✅ Created new keyword: {keyword_name}")

            if trans.keyword != keyword_obj:
                trans.keyword = keyword_obj
                trans.save()
                updated += 1
                print(f"🔄 Updated '{trans.transaction}' → {keyword_name}")
            break  # Stop after first matching keyword

print(f"\n🎉 Finished!")
print(f"✔ Updated {updated} transactions")
print(f"✔ Created {created_keywords} new keywords")




# python manage.py shell < data/transaction_mapping.py
