# Generated by Django 4.1.4 on 2023-04-19 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_productgallery'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sold',
            field=models.IntegerField(default=0),
        ),
    ]
