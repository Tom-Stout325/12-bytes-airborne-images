# reassign_transactions.py

from django.contrib.auth import get_user_model
from finance.models import Transaction

# Set this to your local superuser's username or email
DEV_USERNAME = "your_dev_username"

User = get_user_model()

try:
    dev_user = User.objects.get(username=DEV_USERNAME)
except User.DoesNotExist:
    print(f"❌ User '{tomstout}' does not exist.")
    exit()

# Update all transactions to belong to your dev user
updated_count = Transaction.objects.update(user=dev_user)

print(f"✅ Reassigned {updated_count} transactions to user '{dev_user.username}' (ID={dev_user.id})")
