# Generated by Django 5.2.1 on 2025-06-17 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Amazonclone', '0007_productquestion_review'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productquestion',
            old_name='question',
            new_name='question_text',
        ),
    ]
