# Generated by Django 4.1 on 2023-02-17 18:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0002_userfile_watermarked"),
    ]

    operations = [
        migrations.AddField(
            model_name="userfile",
            name="paid",
            field=models.BooleanField(default=False),
        ),
    ]
