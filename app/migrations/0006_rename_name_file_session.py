# Generated by Django 4.1.5 on 2023-01-09 19:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_file_name"),
    ]

    operations = [
        migrations.RenameField(
            model_name="file",
            old_name="name",
            new_name="session",
        ),
    ]
