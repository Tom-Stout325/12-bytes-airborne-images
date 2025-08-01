# Generated by Django 4.2.20 on 2025-07-13 17:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_remove_keyword_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invoice',
            options={},
        ),
        migrations.RemoveIndex(
            model_name='invoice',
            name='finance_inv_invoice_21faaa_idx',
        ),
        migrations.RemoveIndex(
            model_name='invoice',
            name='finance_inv_date_1aaab4_idx',
        ),
        migrations.RemoveIndex(
            model_name='invoice',
            name='finance_inv_due_860b47_idx',
        ),
        migrations.RemoveIndex(
            model_name='invoice',
            name='finance_inv_paid_da_03a9a9_idx',
        ),
        migrations.RemoveIndex(
            model_name='invoice',
            name='finance_inv_client__37a0c7_idx',
        ),
        migrations.RemoveIndex(
            model_name='invoice',
            name='finance_inv_keyword_1df90a_idx',
        ),
        migrations.RemoveIndex(
            model_name='invoice',
            name='finance_inv_service_6c695b_idx',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='search_vector',
        ),
        migrations.AlterField(
            model_name='invoice',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0.0, editable=False, max_digits=12),
        ),
        migrations.AlterField(
            model_name='invoiceitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='finance.service'),
        ),
        migrations.AlterField(
            model_name='invoiceitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=20),
        ),
        migrations.AlterField(
            model_name='invoiceitem',
            name='qty',
            field=models.IntegerField(default=1),
        ),
    ]
