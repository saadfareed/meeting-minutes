# Generated by Django 3.1 on 2022-04-15 17:17

import cloudinary_storage.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0009_auto_20220415_0611'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voice_record', models.FileField(storage=cloudinary_storage.storage.RawMediaCloudinaryStorage(), upload_to='records')),
            ],
        ),
    ]
