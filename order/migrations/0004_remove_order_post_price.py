# Generated by Django 4.1.4 on 2023-04-14 19:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_alter_order_post_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='post_price',
        ),
    ]
