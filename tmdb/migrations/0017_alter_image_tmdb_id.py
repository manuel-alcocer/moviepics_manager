# Generated by Django 4.1.5 on 2023-01-13 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmdb', '0016_alter_image_tmdb_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='tmdb_id',
            field=models.IntegerField(),
        ),
    ]
