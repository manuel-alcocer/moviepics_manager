# Generated by Django 4.1.5 on 2023-01-13 14:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tmdb', '0023_alter_movie_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='tmdb_id',
        ),
    ]