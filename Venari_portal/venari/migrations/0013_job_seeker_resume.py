# Generated by Django 4.2.7 on 2023-11-25 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venari', '0012_alter_job_seeker_bookmarks'),
    ]

    operations = [
        migrations.AddField(
            model_name='job_seeker',
            name='resume',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]