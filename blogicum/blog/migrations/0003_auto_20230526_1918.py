# Generated by Django 3.2.16 on 2023-05-26 16:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20230526_1902'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='location',
            name='is_published',
        ),
    ]
