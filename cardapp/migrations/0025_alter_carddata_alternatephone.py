# Generated by Django 4.1.5 on 2023-03-01 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardapp', '0024_remove_carddata_middlename_carddata_alternatephone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carddata',
            name='alternatephone',
            field=models.CharField(max_length=11, null=True),
        ),
    ]
