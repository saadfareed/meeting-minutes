# Generated by Django 3.1 on 2022-04-10 14:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_roommember'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roommember',
            name='channel_name',
        ),
        migrations.RemoveField(
            model_name='roommember',
            name='insession',
        ),
        migrations.RemoveField(
            model_name='roommember',
            name='uid',
        ),
    ]
