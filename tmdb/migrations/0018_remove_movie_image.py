# Generated by Django 4.1.5 on 2023-01-13 10:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tmdb', '0017_alter_image_tmdb_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='image',
        ),
    ]
