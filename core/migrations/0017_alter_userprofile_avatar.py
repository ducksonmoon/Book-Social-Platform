# Generated by Django 3.2.6 on 2021-12-14 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_userprofile_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(blank=True, default='defaults/avatar-happy.png', null=True, upload_to='avatars/'),
        ),
    ]
