# Generated by Django 4.1.5 on 2023-01-20 07:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cardapp', '0014_carddata_qr_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carddata',
            name='qr_code',
        ),
    ]
