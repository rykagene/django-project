# Generated by Django 4.2.7 on 2023-11-18 02:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('venari', '0005_post_jobs'),
    ]

    operations = [
        migrations.CreateModel(
            name='apply_job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(default='', max_length=200)),
                ('email', models.CharField(max_length=100, null=True)),
                ('jobtype', models.CharField(max_length=50, null=True)),
                ('resume', models.ImageField(upload_to='')),
                ('apply_date', models.DateField()),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='venari.job_seeker')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='venari.post_jobs')),
            ],
        ),
    ]
