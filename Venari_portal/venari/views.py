from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from . models import *
from django.core.mail import send_mail
from datetime import date
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
import logging
import os
from openpyxl import Workbook
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
import json
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger('venari')

def index(request):
    return render(request, "venarihomepage.html")

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

def pre_register(request):
    return render(request, "pre-register.html")
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
        skills = request.POST['skills']
        address = request.POST['home_address']
        uniqueemail = User.objects.filter(email=email)
        uniqueuser = User.objects.filter(username=username)
        if uniqueemail:
            messages.error(request, "Email exists.")
            return redirect('/register-user')
        elif uniqueuser:
            messages.error(request, "Username exists.")
            return redirect('/register-user')
        elif password != cpass:
            messages.error(request, "Password doesn't match.")
            return redirect('/register-user')

        user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
        applicants = job_seeker.objects.create(user=user, email=email, phone_number=phone, password=password, gender=gender, profile_image=profile_picture, skills=skills, address = address, user_type="applicant", status="Activate")
        user.save()
        applicants.save()
        return render(request, "login.html")
    return render(request, "register-user.html")

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

def jobseeker_workexperience(request):
    if not request.user.is_authenticated:
        return redirect('/user_login/')
    applicant = job_seeker.objects.get(user=request.user)
    if request.method=="POST":   
        company_name = request.POST['company_name']
        company_address = request.POST['company_address']
        position = request.POST['position']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        applicant.company_name = company_name
        applicant.company_address = company_address
        applicant.position = position
        applicant.start_date = start_date
        applicant.end_date = end_date
        applicant.save()
        applicant.user.save()
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
        experience = request.POST['experience']
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
            applicant.years_experience = experience
            applicant.save()
            applicant.user.save()
            return redirect("/jobseeker_profile/")
        
    print(request.FILES)
    return render(request, "jobseeker_profile.html", {'applicant':applicant})
def user_changepassword(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    applicant = job_seeker.objects.get(user=request.user)

    if request.method == "POST":
        new_password = request.POST.get('newPassword')

        # Update the job seeker's password
        applicant.password = new_password
        applicant.save()

        # Update the associated User's password
        user = User.objects.get(username=request.user.username)
        user.set_password(new_password)
        user.save()

    return redirect("/jobseeker_profile")

        
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
def jobseeker_changeprofile(request):
    if not request.user.is_authenticated:
        return redirect('/user_login/')
    applicant = job_seeker.objects.get(user=request.user)
    if request.method=="POST":   
        image = request.FILES['profile_image']
        applicant.profile_image = image
        applicant.save()  
        return redirect("/jobseeker_profile/")
    print(request.FILES)
    return render(request, "jobseeker_profile.html", {'applicant':applicant})
def jobseeker_uploadresume(request):
    if not request.user.is_authenticated:
        return redirect('/user_login/')
    applicant = job_seeker.objects.get(user=request.user)
    if request.method=="POST":   
        resume = request.FILES['resume']
        applicant.resume = resume
        applicant.save()  
        return redirect("/jobseeker_profile/")
    print(request.FILES)
    return render(request, "jobseeker_profile.html", {'applicant':applicant})


def bookmark_job(request, job_id):
    if request.method == 'POST':
        job = get_object_or_404(post_jobs, id=job_id)
        user = job_seeker.objects.get(user=request.user)
        if job.id in user.bookmarks.values_list('id', flat=True):
            user.bookmarks.remove(job)
            success = False
        else:
            user.bookmarks.add(job)
            success = True

        return JsonResponse({'success': success})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
def Logout(request):
    logout(request)
    return redirect('/')

def job_hiring(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    posted_jobs = post_jobs.objects.all()
    result = None

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            search = data.get('search')
            employment_type = data.get('employment_type')
            time_option = data.get('time_option') 
            print(search)
            if search is not None:
                result = posted_jobs.filter(Q(title__icontains=search) | Q(skills__icontains=search))
                
                if employment_type:
                    result = result.filter(jobtype=employment_type)
                if time_option == 'recentlyPosted':
                    result = result.filter(creation_date__gte=timezone.now() - timezone.timedelta(days=1))
                elif time_option == 'last7Days':
                    result = result.filter(creation_date__gte=timezone.now() - timezone.timedelta(days=7))
                elif time_option == 'aWeekAgo':
                    result = result.filter(creation_date__lte=timezone.now() - timezone.timedelta(days=7))
                
                jobs = []
                
                for job in result:
                    job_data = {
                        'id': job.id,
                        'title': job.title,
                        'company_name': job.company.company_name,
                        'company_logo_url': job.company.company_logo.url,
                        'creation_date': job.creation_date,
                        'location': job.location,
                        'jobtype': job.jobtype,
                        'skills': job.skills,
                        'salary': job.salary
                    }
                    jobs.append(job_data)

                return JsonResponse({'jobs': jobs})
        except json.JSONDecodeError:
            pass

    jobs = post_jobs.objects.all().order_by('-start_date')
    applicant = job_seeker.objects.get(user=request.user)
    apply = apply_job.objects.filter(applicant=applicant)
    bookmarked_jobs = {applicant.id: applicant.bookmarks.values_list('id', flat=True) for applicant in [applicant]}
    data = []
    for i in apply:
        data.append(i.job.id)

    return render(request, "job_hiring.html", {'jobs': jobs, 'data': data, 'applicant': applicant, 'bookmark': bookmarked_jobs, 'result': result})
def jobseeker_apply(request, myid):
    if not request.user.is_authenticated:
        return redirect("/login")

    applicant = job_seeker.objects.get(user=request.user)
    job = post_jobs.objects.get(id=myid)
    Company = company.objects.get(id=job.company_id)
    date1 = date.today()

    if job.end_date < date1:
        return JsonResponse({'success': False, 'error': 'The application period is closed.'})
    elif job.start_date > date1:
        return JsonResponse({'success': False, 'error': 'The application period is closed.'})
    else:
        if request.method == "POST":
            # Check if the job seeker has already applied for this job
            existing_application = apply_job.objects.filter(job=job, applicant=applicant).exists()
            
            if not existing_application:
                # If not, create a new application
                apply_job.objects.create(
                    job=job,
                    jobtype=job.jobtype,
                    email=applicant.user.email,
                    company=Company.company_name,
                    applicant=applicant,
                    resume=applicant.resume,
                    apply_date=date.today()
                )
                success = True
            else:
                # If an application already exists, return an error
                success = False
                return JsonResponse({'success': success, 'error': 'Already applied for this job'})

            return JsonResponse({'success': success})

    return render(request, "job_hiring.html", {'job': job})

def jobseeker_delete_account(request, myid):
    if not request.user.is_authenticated:
        return redirect("/login")
    applicant = job_seeker.objects.filter(id=myid)
    applicant.delete()
    messages.success(request, "Successfully deleted.")
    return redirect("/login")


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
            return redirect('/register-company')
        elif uniqueuser:
            messages.error(request, "Username exists.")
            return redirect('/register-company')
        elif password != cpass:
            messages.error(request, "Password doesn't match.")
            return redirect('/register-company')
        elif company.objects.filter(phone_number=phone).exists() or job_seeker.objects.filter(phone_number=phone).exists():
            messages.error(request, "Phone number already exist.")
            return redirect('/register-company')
        elif company.objects.filter(company_name=company_name).exists():
            messages.error(request, "Company name already exist.")
            return redirect('/register-company')

        user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
        company_user = company.objects.create(user=user, email=email, phone_number=phone, password=password, company_name=company_name, company_ceo=company_ceo, company_established=company_established, company_location=company_location,company_logo=company_logo, gender=gender, user_type="company", status="Pending")
        user.save()
        company_user.save()
        #logout(request)
        return render(request, "company_login.html")
    return render(request, "register-company.html")

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
    jobs_posted_count = jobs.count()
    applicant = apply_job.objects.filter(company = companies.company_name)
    applicant_count = applicant.count()
    return render(request, "company_dashboard.html", {'jobs':jobs, 'company':companies, 'applicants': applicant, 'job_posted_count': jobs_posted_count, 'applicant_count': applicant_count})



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

def company_accept_applicant(request, myid):
    
    if not request.user.is_authenticated:
        return redirect("/compnay_login")
    application = apply_job.objects.get(id=myid)
    applicant = job_seeker.objects.get(id=application.applicant_id)
    post = post_jobs.objects.get(id=application.job_id)
    Company = company.objects.get(id=post.company_id)

    if request.method == "POST":
        status = request.POST['status']
        if status == 'hire':
            application.status=status
            application.save()
            send_mail(
                'Invitation for Final Interview',  # subject
                f'Hi {applicant.user.last_name},\n\n'
                f'We are delighted to inform you that {application.company} has reviewed your application for the {application.jobtype} position. '
                f'Based on our initial assessment, we would like to invite you for a final interview to discuss your qualifications and explore the opportunity to work together.\n\n'
                f'Details of the job opening:\n'
                f'- Company Name: {application.company}\n'
                f'- Job Type: {application.jobtype}\n'
                f'- Start Date: {post.start_date}\n'
                f'- End Date: {post.end_date}\n'
                f'- Monthly Salary: {post.salary} pesos\n'
                f'- Experience Required: {post.experience} year/s\n'
                f'- Required Skills: {post.skills}\n\n'
                f'Please let us know your availability for the final interview, and we will schedule a suitable time. If you have any questions or need further information, feel free to reach out.\n\n'
                f'Thank you for your continued interest in joining {application.company}. We look forward to meeting you!\n\n'
                f'Best regards,\n'
                f'{application.company}\n'
                f'{Company.phone_number}',
                'venaricompany@gmail.com',
                [application.email],  
            )
            messages.success(request, "Status changed successfully.")
            return redirect("/company_dashboard")
        else:
            applicant = apply_job.objects.filter(id=myid)
            applicant.delete()
            messages.success(request, "Successfully deleted.")
            return redirect("/company_dashboard")
        
    return render(request, "company_dashboard.html", {'accept':application})

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
            return redirect("/admin_dashboard")
        elif user.is_superuser == False:
            messages.error(request, "Please enter a valid username or password.")
            return redirect('/admin_login')
        else:
            messages.error(request, "Please enter a valid username or password.")
            return redirect('/admin_login')
    return render(request, "login.html")   
 
def all_companies(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            search = data.get('search')
            print(search)
            if search is not None and search.strip() != "":
                results = company.objects.filter(company_name__icontains=search)
            else:
                results = company.objects.all()
    
            companies_data = []
                
            for company_instance in results:
                posted_jobs = post_jobs.objects.filter(company_id=company_instance.id)
                applicant_count = apply_job.objects.filter(job_id__in=posted_jobs.values_list('id', flat=True)).count()
                posted_job_count = posted_jobs.count()
                company_data = {
                    'company_name': company_instance.company_name,
                    'applicants': applicant_count,
                    'posted_jobs': posted_job_count,
                    'company_status': company_instance.status,
                    'company_logo': company_instance.company_logo.url,
                    'company_id': company_instance.id
                }
                companies_data.append(company_data)

            return JsonResponse({'company': companies_data})
        except json.JSONDecodeError:
            pass

        
    status_filter = request.GET.get('status', 'all')
    
    if status_filter == 'all':
        companies = company.objects.all()
    else:
        companies = company.objects.filter(status=status_filter)
        
    accepted_companies_count = companies.filter(status='Accepted').count()

    for Companies in companies:
        posted_jobs = post_jobs.objects.filter(company_id=Companies.id)
        posted_job_count = posted_jobs.count()
        applicant_count = apply_job.objects.filter(job_id__in=posted_jobs.values_list('id', flat=True)).count()
        Companies.applicant_count = applicant_count
        Companies.posted_job_count = posted_job_count

    context = {
        'companies': companies,
        'status_filter': status_filter,
        'all_company': accepted_companies_count
    }
    return render(request, 'companies_list.html', context)



def change_status(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    companies = company.objects.get(id=myid)
    if request.method == "POST":
            try:
                data = json.loads(request.body.decode('utf-8'))
                status = data.get('status') 
                if status is not None:  
                    old_status = companies.status
                    companies.status = status
                    companies.save()
                    messages.success(request, "Status changed successfully.")
                    logger.info(f"Status changed successfully for job ID {myid}. Old status: {old_status}, New status: {status}")
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'Invalid status value'})

            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'Invalid JSON data'})

    return render(request, "admin_dashboard.html", {'company':companies})

def change_status_jobseeker(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    applicant = job_seeker.objects.get(id=myid)
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            status = data.get('status') 
            if status is not None:  
                old_status = applicant.status
                applicant.status = status
                applicant.save()
                messages.success(request, "Status changed successfully.")
                logger.info(f"Status changed successfully for job ID {myid}. Old status: {old_status}, New status: {status}")
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status value'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})

    return render(request, "admin_dashboard.html", {'applicant':applicant})

def delete_company(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    try:
        company_instance = company.objects.get(id=myid)
        post_jobs_instances = post_jobs.objects.filter(company_id=myid)
        if post_jobs_instances.exists():
            post_jobs_instances.delete()

        company_instance.delete()

        messages.success(request, "Successfully deleted.")
        logger.info(f"Company and job postings deleted successfully for company ID {myid}")
        return JsonResponse({'success': True, 'message': 'Company and job postings deleted successfully'})
    except company_instance.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Company not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def delete_user(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_view_jobseeker")
    applicant = job_seeker.objects.filter(id=myid)
    applicant.delete()
    messages.success(request, "Successfully deleted.")
    return redirect("/jobseeker_list")

def view_jobseeker(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            search = data.get('search')
            print(search)
            if search is not None and search.strip() != "":
                results = job_seeker.objects.filter(user__first_name__icontains=search)
            else:
                results = job_seeker.objects.all()
    
            companies_data = []
                
            for applicant_instance in results:
                company_data = {
                    'first_name': applicant_instance.user.first_name,
                    'last_name': applicant_instance.user.last_name,
                    'email': applicant_instance.email,
                    'contact': applicant_instance.phone_number,
                    'status': applicant_instance.status,
                    'image': applicant_instance.profile_image.url,
                    'applicant_id': applicant_instance.id
                }
                companies_data.append(company_data)

            return JsonResponse({'applicant': companies_data})
        except json.JSONDecodeError:
            pass
    applicants = job_seeker.objects.all()
    return render(request, "jobseeker_list.html", {'applicants':applicants})


def admin_job_list(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            search = data.get('search')
            if search is not None and search.strip() != "":
                results = post_jobs.objects.filter(title__icontains=search)
            else:
                results = post_jobs.objects.all()
        
            job_data = []
                    
            for job_instance in results:

                job_data.append({
                    'company_name': job_instance.company.company_name,
                    'job_title': job_instance.title,
                    'job_type': job_instance.jobtype,
                    'creation_date': job_instance.start_date,
                    'job_status': job_instance.status,
                    'job_id': job_instance.id
                })

            return JsonResponse({'jobs': job_data})
        except json.JSONDecodeError:
            pass
        
    jobs = post_jobs.objects.all()
    return render(request, "admin_joblist.html", {'jobs':jobs})

def get_job_data(request, job_id):
    try:
        job = post_jobs.objects.get(id=job_id)
    except post_jobs.DoesNotExist:
        raise Http404("Job does not exist")

    data = {
        'title': job.title,
        'job_id': job_id,
        'start_date': str(job.start_date),
        'end_date': str(job.end_date),
        'experience': job.experience,
        'salary': job.salary,
        'skills': job.skills,
        'jobtype': job.jobtype,
        'location': job.location,
        'description': job.description,
    }

    return JsonResponse(data)

def get_apply_data(request, job_id):
    try:
        apply = apply_job.objects.get(job_id=job_id)
        post = post_jobs.objects.get(id=apply.job_id)
        applicant = job_seeker.objects.get(id=apply.applicant_id)
    except apply_job.DoesNotExist:
        raise Http404("Apply job does not exist")
    except post_jobs.DoesNotExist:
        raise Http404("Post job does not exist")
    except job_seeker.DoesNotExist:
        raise Http404("Job seeker does not exist")
    data = {
        'title': post.title,
        'company': apply.company,
        'job_type': apply.jobtype,
        'applicant_first': applicant.user.first_name,
        'applicant_last': applicant.user.last_name,
        'resume_url': apply.resume.url if apply.resume else None,
    }

    return JsonResponse(data, encoder=DjangoJSONEncoder)

def get_applicant_data(request, job_id):
    try:
        applicant = job_seeker.objects.get(id=job_id)
    except job_seeker.DoesNotExist:
        raise Http404("Applicant does not exist")
    resume_url = applicant.resume.url if applicant.resume else None

    data = {
        'applicant_id': applicant.id,
        'first_name': applicant.user.first_name,
        'last_name': applicant.user.last_name,
        'gender': applicant.gender,
        'username': applicant.user.username,
        'email': applicant.email,
        'contact': applicant.phone_number,
        'address': applicant.address,
    }
    return JsonResponse(data)

def admin_changejob_status(request, myid):
    logger.info(f"Received request to change status for job ID: {myid}")
    
    if not request.user.is_authenticated:
        return redirect("/admin_login")

    job = post_jobs.objects.get(id=myid)

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            status = data.get('status') 
            print(data, status)

            if status is not None:  
                old_status = job.status
                job.status = status
                job.save()
                messages.success(request, "Status changed successfully.")
                logger.info(f"Status changed successfully for job ID {myid}. Old status: {old_status}, New status: {status}")
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status value'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})

    return render(request, "admin_dashboard.html", {'job': job})

def admin_changejob_status(request, myid):
    logger.info(f"Received request to change status for job ID: {myid}")
    
    if not request.user.is_authenticated:
        return redirect("/admin_login")

    job = post_jobs.objects.get(id=myid)
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            status = data.get('status') 
            print(data, status)

            if status is not None:  
                old_status = job.status
                job.status = status
                job.save()
                messages.success(request, "Status changed successfully.")
                logger.info(f"Status changed successfully for job ID {myid}. Old status: {old_status}, New status: {status}")
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status value'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})

    return render(request, "admin_dashboard.html", {'job': job})
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
        return redirect("/admin_login")
    try:
        jobs = post_jobs.objects.get(id=myid)
        jobs.delete()
        messages.success(request, "Successfully deleted.")
        logger.info(f"Company and job postings deleted successfully for company ID {myid}")
        return JsonResponse({'success': True, 'message': 'Company and job postings deleted successfully'})
    except jobs.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Company not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
 
def admin_reject_company(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    try:
        Company = company.objects.get(id=myid)
        Company.delete()
        messages.success(request, "Successfully deleted.")
        logger.info(f"Company and job postings deleted successfully for company ID {myid}")
        return JsonResponse({'success': True, 'message': 'Company and job postings deleted successfully'})
    except Company.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Company not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
  
    

def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    active_company = company.objects.filter(status='Accepted')
    active_company_counts = active_company.count()
    active_jobseeker = job_seeker.objects.filter(status='Activate')
    active_jobseeker_count = active_jobseeker.count()
    active_post = post_jobs.objects.filter(status__in=['Activate', 'Deactivate'])
    active_post_counts = active_post.count()
    
    log_file_path = os.path.join('venari', 'admin_logs', 'logfile.log')

    logs = []
    try:
        with open(log_file_path, 'r') as log_file:
            logs = log_file.read().splitlines()
    except FileNotFoundError:
        pass  

    formatted_logs = []
    for log in logs:
        log_parts = log.split(' ', 5)
        if len(log_parts) == 6:
            timestamp = log_parts[0] + ' ' + log_parts[1]
            log_level = log_parts[2]
            admin_name = log_parts[3]
            action = log_parts[4]
            details = log_parts[5].strip()
            formatted_log = {
                'timestamp': timestamp,
                'log_level': log_level,
                'admin_name': admin_name,
                'action': action,
                'details': details,
            }
            formatted_logs.append(formatted_log)
    context = {
        'all_companies': active_company,
        'all_applicants': active_jobseeker,
        'all_companies_count': active_company_counts,
        'all_jobseeker_count': active_jobseeker_count,
        'all_post': active_post,
        'all_post_counts': active_post_counts,
        'logs': formatted_logs
    }
    return render(request, "admin_dashboard.html", context)
def admin_generate_report(request):
    data = job_seeker.objects.all()
    wb = Workbook()
    ws = wb.active

    header = ['Field 1', 'Field 2']  
    ws.append(header)

    for item in data:
        ws.append([item.email, item.password])  

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=report.xlsx'

    wb.save(response)

    return response

def admin_edit_jobpost(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    if request.method == "POST":
        job_id = request.POST['job_id']
        title = request.POST['job_title']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        salary = request.POST['salary']
        experience = request.POST['experience']
        location = request.POST['location']
        skills = request.POST['skills']
        jobtype = request.POST['jobtype']
        description = request.POST['description']
        
        job_posted = post_jobs.objects.get(id=job_id)
        job_posted.title = title
        job_posted.start_date = start_date
        job_posted.end_date = end_date
        job_posted.salary = salary
        job_posted.experience = experience
        job_posted.location = location
        job_posted.skills = skills
        job_posted.job_type = jobtype
        job_posted.description = description
        job_posted.save()
        return redirect("/admin_joblist")
    
    return render(request, "admin_joblist.html")

def admin_edit_applicant(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    if request.method == "POST":
        applicant_id = request.POST['applicant_id']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        gender = request.POST['gender']
        username = request.POST['username']
        email = request.POST['email']
        contact = request.POST['contact']
        address = request.POST['address']
        
        applicant = job_seeker.objects.get(id=applicant_id)
        applicant.user.first_name=first_name
        applicant.user.last_name=last_name
        applicant.gender=gender
        applicant.user.username=username
        applicant.email = email
        applicant.phone_number=contact
        applicant.address=address
        applicant.save()
        return redirect("/jobseeker_list")
    
    return render(request, "jobseeker_list.html")