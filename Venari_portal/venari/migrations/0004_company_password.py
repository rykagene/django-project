# Generated by Django 4.2.7 on 2023-11-17 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venari', '0003_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='password',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
