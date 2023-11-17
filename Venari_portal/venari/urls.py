from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #job seeker
    path("", views.user_login, name="login"), #change this if landing page is finish
    path("signup/", views.user_signup, name="signup"),

    #admin
    path("admin_login/", views.admin_login, name="admin login"),
    path("admin_delete_company/<int:myid>/", views.delete_company, name="admin login"),

    #company
    path("company_signup/", views.company_signup, name="company signup"),
    path("company_login/", views.company_login, name="company login"),
    path("companies_list/", views.all_companies, name="companies list"),
    path("company_change_status/<int:myid>/", views.change_status, name="company change status"),
    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)