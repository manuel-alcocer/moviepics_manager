# Generated by Django 4.1.5 on 2023-01-13 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filesystem', '0005_file_extension_file_realpath_alter_file_filename'),
    ]

    operations = [
        migrations.RenameField(
            model_name='file',
            old_name='filename',
            new_name='name',
        ),
    ]