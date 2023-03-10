# Generated by Django 4.1.5 on 2023-03-02 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardapp', '0025_alter_carddata_alternatephone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carddata',
            name='firstname',
        ),
        migrations.RemoveField(
            model_name='carddata',
            name='lastname',
        ),
        migrations.AddField(
            model_name='carddata',
            name='cardname',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='carddata',
            name='fullname',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
