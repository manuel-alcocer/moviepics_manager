# Generated by Django 4.1.5 on 2023-01-15 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmdb', '0039_movie_download_error_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='download_error',
        ),
        migrations.AddField(
            model_name='movie',
            name='download_correct',
            field=models.BooleanField(default=True),
        ),
    ]