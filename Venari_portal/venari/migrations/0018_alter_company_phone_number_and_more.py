# Generated by Django 4.2.7 on 2023-12-12 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venari', '0017_job_seeker_experience_job_seeker_years_experience'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='phone_number',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='job_seeker',
            name='phone_number',
            field=models.IntegerField(),
        ),
    ]
