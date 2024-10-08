# Generated by Django 5.1.1 on 2024-10-08 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("customerend", "0002_cartitem_order"),
    ]

    operations = [
        migrations.AddField(
            model_name="cart",
            name="total_price",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
