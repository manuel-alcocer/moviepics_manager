# Generated by Django 4.1.5 on 2023-01-13 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmdb', '0028_image_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='title',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]
