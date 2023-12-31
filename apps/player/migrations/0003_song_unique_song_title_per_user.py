# Generated by Django 4.2.5 on 2023-10-29 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0002_remove_song_date'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='song',
            constraint=models.UniqueConstraint(fields=('artist', 'title'), name='unique_song_title_per_user'),
        ),
    ]
