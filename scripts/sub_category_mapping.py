import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from finance.models import Transaction, Keyword, SubCategory

# ✅ Subcategories that should always get the 'Monthly' keyword
monthly_subcategories = [
    "Other Expenses - Software",
    "Other Expenses - Office Equipment",
    "Other Expense - Education",
    "Utilities - Cellular Service",
    "Insurance - Business Insurance",
    "Other Expenses - Bank Fees",
    "Insurance - Aviation",
]

updated = 0
created_keywords = 0

# ✅ Get or create the 'Monthly' keyword instance
monthly_keyword, created = Keyword.objects.get_or_create(name="Monthly")
if created:
    created_keywords += 1
    print("✅ Created new keyword: Monthly")

# ✅ Update all transactions that have these subcategories
transactions = Transaction.objects.filter(sub_cat__sub_cat__in=monthly_subcategories)

for trans in transactions:
    if trans.keyword != monthly_keyword:
        trans.keyword = monthly_keyword
        trans.save()
        updated += 1
        print(f"🔄 Updated '{trans.transaction}' (SubCategory: {trans.sub_cat.sub_cat}) → Monthly")

print(f"\n🎉 Finished!")
print(f"✔ Updated {updated} transactions")
print(f"✔ Created {created_keywords} new keywords")



# python manage.py shell < data/sub_category_mapping.py
