# Generated by Django 4.1.5 on 2023-04-05 06:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cardapp', '0032_alter_carddata_alternatephone'),
    ]

    operations = [
        migrations.AddField(
            model_name='carddata',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='carddata',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]