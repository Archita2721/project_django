# Generated by Django 4.1.5 on 2023-04-03 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardapp', '0030_alter_carddata_upload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carddata',
            name='alternatephone',
            field=models.CharField(blank=True, max_length=11, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='carddata',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
