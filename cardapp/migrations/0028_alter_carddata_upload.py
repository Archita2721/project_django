# Generated by Django 4.1.5 on 2023-03-30 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardapp', '0027_alter_carddata_alternatephone_alter_carddata_upload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carddata',
            name='upload',
            field=models.FileField(blank=True, null=True, upload_to='uploads'),
        ),
    ]