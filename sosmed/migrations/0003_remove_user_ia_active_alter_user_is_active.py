# Generated by Django 5.1.3 on 2024-12-04 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sosmed', '0002_alter_user_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='ia_active',
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
