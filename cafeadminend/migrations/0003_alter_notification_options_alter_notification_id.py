# Generated by Django 5.1.1 on 2024-10-09 10:03

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cafeadminend", "0002_notification"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="notification",
            options={
                "ordering": ["-updated_at"],
                "verbose_name_plural": "Notifications",
            },
        ),
        migrations.AlterField(
            model_name="notification",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
    ]
