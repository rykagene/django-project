from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('', views.index, name="landing page"), 
    #job seeker
    path('login/', views.user_login, name="login"), 
    path("signup/", views.user_signup, name="signup"),
    path("user_homepage/", views.user_homepage, name="homepage"),
    path('logout/', views.Logout, name='logout'),


    #admin
    path("admin_login/", views.admin_login, name="admin login"),
    path("admin_delete_company/<int:myid>/", views.delete_company, name="admin login"),
    path("company_change_status/<int:myid>/", views.change_status, name="company change status"),

    #company
    path("company_signup/", views.company_signup, name="company signup"),
    path("company_login/", views.company_login, name="company login"),
    path("companies_list/", views.all_companies, name="companies list"),
    path("company_post_job/", views.company_post_job, name="companies list"),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)