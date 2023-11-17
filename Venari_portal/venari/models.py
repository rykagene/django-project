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

    