# Generated by Django 3.1.7 on 2021-04-26 16:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0004_order_get_cost'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='get_cost',
        ),
    ]
