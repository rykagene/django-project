# Generated by Django 4.2.7 on 2023-11-17 02:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('venari', '0002_rename_user_id_job_seeker_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=100, null=True)),
                ('phone_number', models.IntegerField(max_length=20)),
                ('company_logo', models.ImageField(upload_to='')),
                ('gender', models.CharField(max_length=10, null=True)),
                ('user_type', models.CharField(max_length=30)),
                ('company_name', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=50, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
