# Generated by Django 4.2.7 on 2023-11-25 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venari', '0011_alter_job_seeker_bookmarks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job_seeker',
            name='bookmarks',
            field=models.ManyToManyField(blank=True, to='venari.post_jobs'),
        ),
    ]
