# Generated by Django 4.1.5 on 2023-01-13 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmdb', '0003_alter_image_movie'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='static/images/'),
        ),
    ]