# Generated by Django 3.2.16 on 2023-06-20 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_post_is_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(verbose_name='Текст комментария'),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='post_images/'),
        ),
    ]