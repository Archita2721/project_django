# Generated by Django 4.1.5 on 2023-01-23 05:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cardapp', '0020_alter_carddata_qr_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carddata',
            name='qr_code',
        ),
    ]
