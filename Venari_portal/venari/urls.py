from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('', views.index, name="landing page"), 
    #job seeker
    path('login/', views.user_login, name="login"), 
    path("pre-register/",views.pre_register ,name="pre-register"),
    path("register-user/", views.user_signup, name="user_signup"),
    path("job_hiring/", views.job_hiring, name="posted jobs"),
    path("jobseeker_profile/", views.jobseeker_profile, name="jobseeker_Edit_profile"),
    path("jobseeker_introduction/", views.jobseeker_introduction, name="jobseeker_introduction"),
    path("jobseeker_basicInformation/", views.jobseeker_basicinformation, name="jobseeker_basicInformation"),
    path("jobseeker_uploadresume/", views.jobseeker_uploadresume, name="jobseeker_uploadresume"),
    path("jobseeker_changeprofile/", views.jobseeker_changeprofile, name="jobseeker_changeprofile"),
    path("jobseeker_changepassword/", views.user_changepassword, name="jobseeker_changepassword"),
    path('bookmark/<int:job_id>/', views.bookmark_job, name='bookmark_job'),
    path("jobseeker_apply/<int:myid>/", views.jobseeker_apply, name="jobseeker_apply"),
    path('logout/', views.Logout, name='logout'),


    #admin
    path("admin_login/", views.admin_login, name="admin login"),
    path("admin_delete_company/<int:myid>/", views.delete_company, name="admin login"),
    path("company_change_status/<int:myid>/", views.change_status, name="company change status"),
    path("jobseeker_list/", views.view_jobseeker, name="edit jobseeker status"),
    path("jobseeker_change_status/<int:myid>/", views.change_status_jobseeker, name="edit jobseeker status"),
    path("admin_joblist/", views.admin_job_list, name="admin list of posted jobs"),
    path("admin_edit_jobpost/<int:myid>/", views.edit_job_admin, name="edit posted job"),
    path("admin_changejob_status/<int:myid>/", views.admin_changejob_status, name="changejob_status"),
    path("admin_delete_postjob/<int:myid>/", views.admin_delete_postjob, name="delete posted job status"),
    path("companies_list/", views.all_companies, name="companies list"),
    path("admin_dashboard/", views.admin_dashboard, name="admin dashboard"),
    path("admin_report/", views.admin_generate_report, name="admin report"),


    #company
    path("register-company/", views.company_signup, name="company signup"),
    path("company_login/", views.company_login, name="company login"),
    path("company_post_job/", views.company_post_job, name="companies list"),
    path("company_profile/", views.company_profile, name="company profile"),
    path("company_dashboard/", views.company_dashboard, name="company dashboard"),
    path("company_accept_applicant/<int:myid>/", views.company_accept_applicant, name="company_accept_applicant"),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)