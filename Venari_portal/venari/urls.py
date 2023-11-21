from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('', views.index, name="landing page"), 
    #job seeker
    path('login/', views.user_login, name="login"), 
    path("signup/", views.user_signup, name="signup"),
    path("job_hiring/", views.job_hiring, name="posted jobs"),
    path("jobseeker_profile/", views.jobseeker_profile, name="job seeker profile"),
    path('logout/', views.Logout, name='logout'),


    #admin
    path("admin_login/", views.admin_login, name="admin login"),
    path("admin_delete_company/<int:myid>/", views.delete_company, name="admin login"),
    path("company_change_status/<int:myid>/", views.change_status, name="company change status"),
    path("admin_view_jobseeker/", views.view_jobseeker, name="edit jobseeker status"),
    path("jobseeker_change_status/<int:myid>/", views.change_status_jobseeker, name="edit jobseeker status"),
    path("admin_joblist/", views.admin_job_list, name="admin list of posted jobs"),
    path("admin_edit_jobpost/<int:myid>/", views.edit_job_admin, name="edit posted job"),
    path("admin_changejob_status/<int:myid>/", views.admin_changejob_status, name="edit posted job status"),
    path("admin_delete_postjob/<int:myid>/", views.admin_delete_postjob, name="delete posted job status"),
    
    #company
    path("company_signup/", views.company_signup, name="company signup"),
    path("company_login/", views.company_login, name="company login"),
    path("companies_list/", views.all_companies, name="companies list"),
    path("company_post_job/", views.company_post_job, name="companies list"),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)