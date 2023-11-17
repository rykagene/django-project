from django.db import models
from django.contrib.auth.models import User

#login and sisgnup for normal user
class job_seeker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, null = True)
    password = models.CharField(max_length=100, null= True)
    email = models.CharField(max_length=100, null=True)
    phone_number = models.IntegerField(max_length=20)
    profile_image = models.ImageField(upload_to="")
    gender = models.CharField(max_length=10, null=True)
    user_type = models.CharField(max_length=30)

    def __str__(self):
        return self.user_id.first_name

#login and signup for company user
class company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.IntegerField(max_length=20)
    email = models.CharField(max_length=100, null=True)
    password = models.CharField(max_length=100, null= True)
    phone_number = models.IntegerField(max_length=20)
    company_logo = models.ImageField(upload_to="")
    gender = models.CharField(max_length=10, null=True)
    user_type = models.CharField(max_length=30)
    company_name = models.CharField(max_length=100)
    status = models.CharField(max_length=50, null = True)

    def __str__(self):
        return self.user.username

class post_jobs(models.Model):
    company = models.ForeignKey(company, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    title = models.CharField(max_length=200)
    jobtype = models.CharField(max_length=50, null = True)
    salary = models.FloatField()
    image = models.ImageField(upload_to="")
    description = models.TextField(max_length=400)
    experience = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, null=True)
    skills = models.CharField(max_length=200)
    creation_date = models.DateField()

    def __str__ (self):
        return self.title
    