# Generated by Django 4.2.7 on 2023-11-25 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venari', '0008_job_seeker_address_job_seeker_age_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='job_seeker',
            name='bio',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
