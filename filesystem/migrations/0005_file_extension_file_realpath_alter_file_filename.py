# Generated by Django 4.1.5 on 2023-01-13 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filesystem', '0004_rename_name_file_filename'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='extension',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='file',
            name='realpath',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='filename',
            field=models.CharField(max_length=255),
        ),
    ]
