# Generated by Django 3.1.7 on 2021-04-27 18:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0008_order_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='town',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
    ]
