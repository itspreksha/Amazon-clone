# Generated by Django 5.2.1 on 2025-06-24 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Amazonclone', '0016_review_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='review_images/'),
        ),
    ]
