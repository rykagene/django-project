from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from . models import *
from django.core.mail import send_mail
from datetime import date
from django.http import JsonResponse


def index(request):
    return render(request, "index.html")

def user_login(request):
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
                return redirect("/job_hiring")  
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
            return redirect('/pre-register')
        elif uniqueuser:
            messages.error(request, "Username exists.")
            return redirect('/pre-register')
        elif password != cpass:
            messages.error(request, "Password doesn't match.")
            return redirect('/pre-register')

        user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
        applicants = job_seeker.objects.create(user=user, email=email, phone_number=phone, password=password, gender=gender, profile_image=profile_picture, user_type="applicant", status="Activate")
        user.save()
        applicants.save()
        return render(request, "login.html")
    return render(request, "pre-register.html")

def jobseeker_profile(request):
    if not request.user.is_authenticated:
        return redirect('/user_login/')
    applicant = job_seeker.objects.get(user=request.user)
    if request.method=="POST":   
        username = request.POST['username']
        email = request.POST['email']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        phone_number = request.POST['phone_number']
        gender = request.POST['gender']
        status = request.POST['status']
        hidden_username = request.POST['hidden_username']
        hidden_email = request.POST['hidden_email']
        hidden_phone = request.POST['hidden_phone']
        uniqueemail = User.objects.filter(email=email)
        uniqueuser = User.objects.filter(username=username)
        if uniqueemail and email != hidden_email:
            error_message = "Email already exists."
            return JsonResponse({'error': error_message})
        elif uniqueuser and username != hidden_username:
            error_message = "Username already exist."
            return JsonResponse({'error': error_message})
        elif (job_seeker.objects.filter(phone_number=phone_number).exists() or company.objects.filter(phone_number=phone_number).exists()) and phone_number != hidden_phone:
            error_message = "Phone number already exists."
            return JsonResponse({'error': error_message})        
        else:
            applicant.user.username = username
            applicant.user.email = email
            applicant.user.first_name = first_name
            applicant.user.last_name = last_name
            applicant.phone_number = phone_number
            applicant.gender = gender
            applicant.status = status
            applicant.save()
            applicant.user.save()
            try:
                image = request.FILES['profile_image']
                applicant.profile_image = image
                applicant.save()
            except Exception as e:
                print(f"Error during image upload: {e}")
                pass
                
            return redirect("/jobseeker_profile/")
    print(request.FILES)
    return render(request, "jobseeker_profile.html", {'applicant':applicant})

def jobseeker_basicinformation(request):
    if not request.user.is_authenticated:
        return redirect('/user_login/')
    applicant = job_seeker.objects.get(user=request.user)
    if request.method=="POST":   
        email = request.POST['email']
        age = request.POST['age']
        home_address = request.POST['home_address']
        phone_number = request.POST['phone_number']
        hidden_email = request.POST['hidden_email']
        hidden_phone = request.POST['hidden_phone']
        uniqueemail = User.objects.filter(email=email)
        if uniqueemail and email != hidden_email:
            error_message = "Email already exists."
            return JsonResponse({'error': error_message})
        elif (job_seeker.objects.filter(phone_number=phone_number).exists() or company.objects.filter(phone_number=phone_number).exists()) and phone_number != hidden_phone:
            error_message = "Phone number already exists."
            return JsonResponse({'error': error_message})        
        else:
            applicant.user.email = email
            applicant.phone_number = phone_number
            applicant.age = age
            applicant.address = home_address
            applicant.save()
            applicant.user.save()
            return redirect("/jobseeker_profile/")
        
    print(request.FILES)
    return render(request, "jobseeker_profile.html", {'applicant':applicant})

def jobseeker_introduction(request):
    if not request.user.is_authenticated:
        return redirect('/user_login/')
    applicant = job_seeker.objects.get(user=request.user)
    if request.method=="POST":   
        username = request.POST['username']
        occupation = request.POST['occupation']
        bio = request.POST['bio']
        hidden_username = request.POST['hidden_username']
        uniqueuser = User.objects.filter(username=username)
        if uniqueuser and username != hidden_username:
            error_message = "Username already exist."
            return JsonResponse({'error': error_message})   
        else:
            applicant.user.username = username
            applicant.occupation = occupation
            applicant.bio = bio
            applicant.save()
            applicant.user.save()

            return redirect("/jobseeker_profile/")
    print(request.FILES)
    return render(request, "jobseeker_profile.html", {'applicant':applicant})

def Logout(request):
    logout(request)
    return redirect('/')

def job_hiring(request):
    jobs = post_jobs.objects.all().order_by('-start_date')
    applicant = job_seeker.objects.get(user=request.user)
    apply = apply_job.objects.filter(applicant=applicant)
    data = []
    for i in apply:
        data.append(i.job.id)
    return render(request, "job_hiring.html", {'jobs':jobs, 'data':data, 'applicant': applicant})

#Company side
def company_signup(request):
    if request.method=="POST":   
        username = request.POST['username']
        company_name = request.POST['company_name']
        company_ceo = request.POST['company_ceo']
        company_established = request.POST['company_established']
        company_location = request.POST['company_location']
        email = request.POST['email']
        first_name=request.POST['first_name']
        last_name = request.POST['last_name']
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
        company_user = company.objects.create(user=user, email=email, phone_number=phone, password=password, company_name=company_name, company_ceo=company_ceo, company_established=company_established, company_location=company_location,company_logo=company_logo, gender=gender, user_type="company", status="Pending")
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
                return redirect("/company_dashboard")
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

def company_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("/company_login")
    companies = company.objects.get(user=request.user)
    jobs = post_jobs.objects.filter(company=companies)
    return render(request, "company_dashboard.html", {'jobs':jobs})

def company_profile(request):
    if not request.user.is_authenticated:
        return redirect("/company_login")
    company_user = company.objects.get(user=request.user)
    if request.method=="POST":   
        username = request.POST['username']
        email = request.POST['email']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        phone_number = request.POST['phone_number']
        gender = request.POST['gender']
        hidden_username = request.POST['hidden_username']
        hidden_email = request.POST['hidden_email']
        hidden_phone = request.POST['hidden_phone']
        uniqueemail = User.objects.filter(email=email)
        uniqueuser = User.objects.filter(username=username)
        if uniqueemail and email != hidden_email:
            messages.error(request, "Email exists.")
            return redirect('/company_profile')
        elif uniqueuser and username != hidden_username:
            messages.error(request, "Username exists.")
            return redirect('/company_profile')
        elif (job_seeker.objects.filter(phone=phone_number).exists() or company.objects.filter(phone=phone_number).exists()) and phone_number != hidden_phone:
            messages.error(request, "Phone number exists.")
            return redirect('/company_profile')
        else:
            company_user.user.username = username
            company_user.email = email
            company_user.user.first_name = first_name
            company_user.user.last_name = last_name
            company_user.phone_number = phone_number
            company_user.gender = gender
            company_user.user.save()
            company_user.save()

            try:
                image = request.FILES['image']
                company_user.company_logo = image
                company_user.save()
            except:
                pass
            alert = True
            return render(request, "company_profile.html", {'alert':alert})
    return render(request, "company_profile.html", {'company':company_user})


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
                [email],  # list of recipient email addresses
            )
        alert = True
        return render(request, "company_post_job.html", {'alert':alert})
    return render(request, "company_post_job.html")



#Admin Side
def admin_login(request):
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

def delete_user(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_view_jobseeker")
    applicant = job_seeker.objects.filter(id=myid)
    applicant.delete()
    messages.success(request, "Successfully deleted.")
    return redirect("/admin_view_jobseeker")

def view_jobseeker(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    applicants = job_seeker.objects.all()
    return render(request, "admin_view_jobseeker.html", {'applicants':applicants})

def change_status_jobseeker(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    applicant = job_seeker.objects.get(id=myid)
    if request.method == "POST":
        status = request.POST['status']
        applicant.status=status
        applicant.save()
        messages.success(request, "Status changed successfully.")
        return redirect("/admin_view_jobseeker")
    return render(request, "jobseeker_change_status.html", {'applicant':applicant})


def admin_job_list(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    jobs = post_jobs.objects.all()
    return render(request, "admin_joblist.html", {'jobs':jobs})


def admin_changejob_status(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    job = post_jobs.objects.get(id=myid)
    if request.method == "POST":
        status = request.POST['status']
        job.status=status
        job.save()
        messages.success(request, "Status changed successfully.")
        return redirect("/admin_joblist")
    return render(request, "admin_changejob_status.html", {'job':job})

def edit_job_admin(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    job = post_jobs.objects.get(id=myid)
    if request.method == "POST":
        title = request.POST['job_title']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        salary = request.POST['salary']
        experience = request.POST['experience']
        location = request.POST['location']
        skills = request.POST['skills']
        description = request.POST['description']
        jobtype = request.POST['jobtype']
        job.title = title
        job.salary = salary
        job.experience = experience
        job.location = location
        job.jobtype = jobtype
        job.skills = skills
        job.description = description

        job.save()
        if start_date:
            job.start_date = start_date
            job.save()
        if end_date:
            job.end_date = end_date
            job.save()
        alert = True
        return render(request, "admin_edit_jobpost.html", {'alert':alert})
    return render(request, "admin_edit_jobpost.html", {'job':job})

def admin_delete_postjob(request, myid):
    if not request.user.is_authenticated:
        return redirect("/company_login")
    jobs = post_jobs.objects.get(id=myid)
    jobs.delete()
    messages.success(request, "Successfully deleted.")
    return redirect("/admin_joblist")