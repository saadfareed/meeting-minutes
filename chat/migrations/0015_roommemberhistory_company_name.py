# Generated by Django 3.1 on 2022-04-29 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0014_auto_20220429_0324'),
    ]

    operations = [
        migrations.AddField(
            model_name='roommemberhistory',
            name='company_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
