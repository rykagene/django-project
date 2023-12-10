from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from . models import *
from django.core.mail import send_mail
from datetime import date
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import logging
import os

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
        # Check if the job is already bookmarked
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
    jobs = post_jobs.objects.all().order_by('-start_date')
    applicant = job_seeker.objects.get(user=request.user)
    apply = apply_job.objects.filter(applicant=applicant)
    bookmarked_jobs = {applicant.id: applicant.bookmarks.values_list('id', flat=True) for applicant in [applicant]}
    data = []
    for i in apply:
        data.append(i.job.id)
    return render(request, "job_hiring.html", {'jobs':jobs, 'data':data, 'applicant': applicant, 'bookmark': bookmarked_jobs})
def jobseeker_apply(request, myid):
    if not request.user.is_authenticated:
        return redirect("/user_login")

    applicant = job_seeker.objects.get(user=request.user)
    job = post_jobs.objects.get(id=myid)
    Company = company.objects.get(id=job.company_id)
    date1 = date.today()

    if job.end_date < date1:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    elif job.start_date > date1:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
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
    applicant = apply_job.objects.filter(company=companies)
    return render(request, "company_dashboard.html", {'jobs':jobs, 'company':companies, 'applicants': applicant})



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
                'venaricompany@gmail.com',  # from_email
                [application.email],  # list of recipient email addresses
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
            logger.info(f"Admin {username} logged in.")
            return redirect("/admin_dashboard")
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
    return redirect("/jobseeker_list")

def view_jobseeker(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    applicants = job_seeker.objects.all()
    return render(request, "jobseeker_list.html", {'applicants':applicants})

def change_status_jobseeker(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    applicant = job_seeker.objects.get(id=myid)
    if request.method == "POST":
        status = request.POST['status']
        applicant.status=status
        applicant.save()
        messages.success(request, "Status changed successfully.")
        return redirect("/jobseeker_list")
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

def admin_dashboard(request):
    active_company = company.objects.filter(status='Accepted')
    active_company_counts = active_company.count()
    active_jobseeker = job_seeker.objects.filter(status='Activate')
    active_jobseeker_count = active_jobseeker.count()
    active_post = post_jobs.objects.filter(status='Activate')
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

    