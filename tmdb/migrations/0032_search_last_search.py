# Generated by Django 4.1.5 on 2023-01-14 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmdb', '0031_alter_image_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='search',
            name='last_search',
            field=models.DateTimeField(auto_now=True),
        ),
    ]