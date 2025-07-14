from finance.models import Transaction, Keyword
from django.db.models import Q

# Keywords from your list (normalized for matching)
keyword_names = [
    "Gainesville", "Arizona", "Pomona I", "Vegas I", "Charlotte I", "Chicago",
    "Epping", "Bristol", "Richmond", "Norwalk", "Seattle", "Sonoma",
    "Brainerd", "Indy", "Reading", "Charlotte II", "St Louis", "Dallas",
    "Georgia", "Vegas II", "Pomona II"
]

for name in keyword_names:
    # Handle casing and spacing safely
    search_term = name.lower().replace(" ", "")
    keyword = Keyword.objects.filter(name__iexact=name).first()
    if keyword:
        updated = Transaction.objects.filter(
            keyword__isnull=True
        ).filter(
            transaction__iregex=rf'\\b{name}\\b'
        ).update(keyword=keyword)
        print(f"✅ {updated} transactions matched and updated with keyword '{name}'")
    else:
        print(f"❌ Keyword '{name}' does not exist.")
