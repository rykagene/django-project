# Generated by Django 4.2.7 on 2023-11-25 01:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venari', '0007_company_company_ceo_company_company_established_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='job_seeker',
            name='address',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='job_seeker',
            name='age',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='job_seeker',
            name='occupation',
            field=models.CharField(max_length=100, null=True),
        ),
    ]