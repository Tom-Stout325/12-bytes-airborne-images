from django.db import migrations

def migrate_trans_type(apps, schema_editor):
    Transaction = apps.get_model('finance', 'Transaction')
    for t in Transaction.objects.all():
        if t.old_trans_type:
            if t.old_trans_type.trans_type == 'Income':
                t.trans_type = 'Income'
            elif t.old_trans_type.trans_type == 'Expense':
                t.trans_type = 'Expense'
            t.save()

class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0005_auto_20250703_1237'),
    ]

    operations = [
        migrations.RunPython(migrate_trans_type),
    ]
