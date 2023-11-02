from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.AdminLogin.as_view(), name="admin_login"),
    path('admin_logout/', views.AdminUserLogout.as_view(), name="admin_logout"),
    path('user_list/', views.UserManagement.as_view(), name="user_list"),
    path('alter_user_status/<str:user_id>', views.AlterUserStatus.as_view(), name="alter_user_status"),

]
