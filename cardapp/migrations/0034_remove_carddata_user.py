# Generated by Django 4.1.5 on 2023-04-05 06:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cardapp', '0033_carddata_user_alter_carddata_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carddata',
            name='user',
        ),
    ]
