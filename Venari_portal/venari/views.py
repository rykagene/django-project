from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from . models import *
from django.core.mail import send_mail
from datetime import date

def index(request):
    return render(request, "index.html")

def user_login(request):
    if request.user.is_authenticated:
        return redirect("/login")
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            is_email = '@' in username
            try:
               #account exist
                if is_email:
                    try:
                        user = authenticate(username=job_seeker.objects.get(email=username).user.username, password=password)
                    except job_seeker.DoesNotExist:
                        user = None
                else:
                    try:
                        user = authenticate(username=User.objects.get(username=username), password=password)
                    except User.DoesNotExist:
                        user = None
            except User.DoesNotExist:
                #account didnt exist
                user = None
            #invalid username/password
            if user is None:
                messages.error(request, "Please enter a valid username or password.")
                return redirect('/login')
            elif user.is_superuser:
                messages.error(request, "Please enter a valid username or password.")
                return redirect('/login')
            
            else:
                #check for login if it activate or not
                try:
                    user1 = job_seeker.objects.get(user=user)
                except:
                    user1 = company.objects.get(user=user)    
                if user1.user_type == "applicant" and user1.status=="Activate":
                    login(request, user)
                    return redirect("/user_homepage")  
                elif user1.user_type == "applicant" and user1.status=="Deactivate":
                    messages.error(request, "Account is deactivated. Please contact the admin.")
                    return redirect('/login')
                elif user1.user_type == "company":
                    messages.error(request, "Please enter a valid username or password.")
                    return redirect('/login')
                else:
                    messages.error(request, "Please enter a valid username or password.")
                    return redirect('/login')      

    return render(request, "login.html")

def user_signup(request):
    if request.method=="POST":   
        username = request.POST['username']
        email = request.POST['email']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        password = request.POST['password']
        cpass = request.POST['confirm_password']
        phone = request.POST['phone_number']
        profile_picture = request.FILES['profile_picture']
        gender = request.POST['gender']
        uniqueemail = User.objects.filter(email=email)
        uniqueuser = User.objects.filter(username=username)
        if uniqueemail:
            messages.error(request, "Email exists.")
            return redirect('/signup')
        elif uniqueuser:
            messages.error(request, "Username exists.")
            return redirect('/signup')
        elif password != cpass:
            messages.error(request, "Password doesn't match.")
            return redirect('/signup')

        user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
        applicants = job_seeker.objects.create(user=user, email=email, phone_number=phone, password=password, gender=gender, profile_image=profile_picture, user_type="applicant", status="Activate")
        user.save()
        applicants.save()
        return render(request, "login.html")
    return render(request, "signup.html")

def user_homepage(request):
    username = request.user.username
    context = {'username': username}
    return render(request, 'user_homepage.html', context)

def Logout(request):
    logout(request)
    return redirect('/')

#Company side
def company_signup(request):
    if request.method=="POST":   
        username = request.POST['username']
        company_name = request.POST['company_name']
        email = request.POST['email']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        password = request.POST['password']
        cpass = request.POST['confirm_password']
        phone = request.POST['phone_number']
        gender = request.POST['gender']
        company_logo = request.FILES['company_logo']
        uniqueemail = User.objects.filter(email=email)
        uniqueuser = User.objects.filter(username=username)
        
        if uniqueemail:
            messages.error(request, "Email exists.")
            return redirect('/company_login')
        elif uniqueuser:
            messages.error(request, "Username exists.")
            return redirect('/company_login')
        elif password != cpass:
            messages.error(request, "Password doesn't match.")
            return redirect('/company_login')
        elif company.objects.filter(phone_number=phone).exists() or job_seeker.objects.filter(phone_number=phone).exists():
            messages.error(request, "Phone number already exist.")
            return redirect('/company_login')
        elif company.objects.filter(company_name=company_name).exists():
            messages.error(request, "Company name already exist.")
            return redirect('/company_login')

        user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
        company_user = company.objects.create(user=user, email=email, phone_number=phone, password=password, company_name=company_name, company_logo=company_logo, gender=gender, user_type="company", status="Pending")
        user.save()
        company_user.save()
        #logout(request)
        return render(request, "company_login.html")
    return render(request, "company_signup.html")

def company_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = authenticate(username=User.objects.get(email=username), password=password)
        except:
            user = authenticate(username=username, password=password)
        if user is None:
            messages.error(request, "Please enter a valid username or password.")
            return redirect('/company_login')
        elif user.is_superuser:
            messages.error(request, "Please enter a valid username or password.")
            return redirect('/company_login')
        else:
            try:
                user1 = job_seeker.objects.get(user=user)
            except:
                user1 = company.objects.get(user=user)    
            if user1.user_type == "company" and user1.status == "Accepted":
                login(request, user)
                #change to main_page
                return redirect("/company_post_job")
            elif user1.user_type == "company" and user1.status == "Pending":
                messages.error(request, "Account is still pending. Please contact the admin.")
                return redirect('/company_login')
            elif user1.user_type == "company" and user1.status == "Rejected":
                messages.error(request, "Account is rejected or deactivated. Please contact the admin.")
                return redirect('/company_login')
            elif user1.user_type == "applicant":
                messages.error(request, "Please enter a valid username or password.")
                return redirect('/company_login')                            
            else:
                messages.error(request, "Please enter a valid username or password.")
                return redirect('/company_login')                         
    return render(request, "company_login.html")

def company_post_job(request):
    if not request.user.is_authenticated:
        return redirect("/company_login")
    if request.method == "POST":
        title = request.POST['job_title']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        salary = request.POST['salary']
        experience = request.POST['experience']
        location = request.POST['location']
        skills = request.POST['skills']
        jobtype = request.POST['jobtype']
        description = request.POST['description']
        user = request.user
        Company = company.objects.get(user=user)
        job_posted = post_jobs.objects.create(company=Company, title=title,start_date=start_date, end_date=end_date, jobtype=jobtype, salary=salary, image=Company.company_logo, experience=experience, location=location, skills=skills, description=description, creation_date=date.today(), status="Activate")
        job_posted.save()
        emails = job_seeker.objects.values_list('email', flat=True)
        for email in emails:
            send_mail(
                'New Job Offer',  # subject
                ('Company ' + str(Company.company_name) + ' posted a new ' + str(jobtype) + ' job that will open at ' + str(start_date) + ' and ends at ' + str(end_date) + '. With a monthly salary of ' + str(salary) + ' pesos. That requires ' + str(experience) + ' year/s of experience with the skill of ' + str(skills) + '.'),
                'ecsoriano.truckings@gmail.com',  # from_email
                [email, "billy.andrade.l@bulsu.edu.ph"],  # list of recipient email addresses
            )
        alert = True
        return render(request, "company_post_job.html", {'alert':alert})
    return render(request, "company_post_job.html")



#Admin Side
def admin_login(request):
    if request.user.is_authenticated:
        messages.error(request, "Already logged in.")
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            try:
                user = authenticate(username=User.objects.get(email=username), password=password)
            except:
                user = authenticate(username=username, password=password)
            if user is None:
                messages.error(request, "Please enter a valid username or password.")
                return redirect('/admin_login')
            elif user.is_superuser:
                login(request, user)
                return redirect("/companies_list")
            elif user.is_superuser == False:
                messages.error(request, "Please enter a valid username or password.")
                return redirect('/admin_login')
            else:
                messages.error(request, "Please enter a valid username or password.")
                return redirect('/admin_login')
    return render(request, "login.html")   
 
def all_companies(request):
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'all':
        companies = company.objects.all()
    else:
        companies = company.objects.filter(status=status_filter)

    context = {
        'companies': companies,
        'status_filter': status_filter,
    }
    return render(request, 'companies_list.html', context)

def change_status(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    companies = company.objects.get(id=myid)
    if request.method == "POST":
        status = request.POST['status']
        companies.status=status
        companies.save()
        messages.success(request, "Status changed successfully.")
        return redirect("/companies_list")
    return render(request, "company_change_status.html", {'company':companies})

def delete_company(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    company = User.objects.filter(id=myid)
    company.delete()
    messages.success(request, "Successfully deleted.")
    return redirect("/companies_list")