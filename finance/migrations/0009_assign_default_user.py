from django.db import migrations

def assign_user(apps, schema_editor):
    Transaction = apps.get_model('finance', 'Transaction')
    User = apps.get_model('auth', 'User')

    try:
        user = User.objects.get(username='tomstout')  # change if needed
    except User.DoesNotExist:
        return  # skip if user not found

    for transaction in Transaction.objects.filter(user__isnull=True):
        transaction.user = user
        transaction.save()

class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0008_transaction_user'),  # replace with your actual latest migration
    ]

    operations = [
        migrations.RunPython(assign_user),
    ]
