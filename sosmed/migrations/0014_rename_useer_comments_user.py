# Generated by Django 5.1.3 on 2024-12-08 03:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sosmed', '0013_comments'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comments',
            old_name='useer',
            new_name='user',
        ),
    ]
