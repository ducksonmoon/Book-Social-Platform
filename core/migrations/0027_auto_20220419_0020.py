# Generated by Django 3.2.6 on 2022-04-19 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_book_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='source_link',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='cover',
            field=models.ImageField(blank=True, null=True, upload_to='covers/'),
        ),
    ]
