# Generated by Django 4.1.4 on 2023-04-14 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_remove_order_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='post_price',
            field=models.FloatField(default=25000),
        ),
    ]
