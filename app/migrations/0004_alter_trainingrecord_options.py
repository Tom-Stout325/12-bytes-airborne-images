# Generated by Django 4.2.20 on 2025-04-20 23:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_pilotprofile_license_date_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trainingrecord',
            options={'ordering': ['-date_completed']},
        ),
    ]
