# Generated by Django 4.2.7 on 2023-11-16 20:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('venari', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job_seeker',
            old_name='user_id',
            new_name='user',
        ),
    ]
