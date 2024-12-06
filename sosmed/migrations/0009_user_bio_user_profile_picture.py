# Generated by Django 5.1.3 on 2024-12-06 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sosmed', '0008_remove_user_bio_remove_user_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, default='profile.png', upload_to='profile_picture/'),
        ),
    ]
