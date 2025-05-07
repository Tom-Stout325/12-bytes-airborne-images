from django.db import migrations, models
import datetime

def convert_paid_string_to_date(apps, schema_editor):
    Invoice = apps.get_model('finance', 'Invoice')

    for invoice in Invoice.objects.all():
        paid = getattr(invoice, 'paid', None)
        if paid and paid.lower() != "no":
            try:
                invoice.paid_date = datetime.datetime.strptime(paid, "%Y-%m-%d").date()
                invoice.status = 'Paid'
            except Exception:
                invoice.paid_date = None
                invoice.status = 'Unpaid'
        else:
            invoice.paid_date = None
            invoice.status = 'Unpaid'

        invoice.save()

class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0010_alter_transaction_user'),  # replace with actual previous migration
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='paid_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('Unpaid', 'Unpaid'), ('Paid', 'Paid'), ('Partial', 'Partial')], default='Unpaid', max_length=20),
        ),
        migrations.RunPython(convert_paid_string_to_date),
        migrations.RemoveField(
            model_name='invoice',
            name='paid',
        ),
    ]
