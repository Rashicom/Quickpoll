from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.AdminLogin.as_view(), name="admin_login"),
    path('admin_logout/', views.AdminUserLogout.as_view(), name="admin_logout"),
    path('user_list/', views.UserManagement.as_view(), name="user_list"),
    path('alter_user_status/<str:user_id>', views.AlterUserStatus.as_view(), name="alter_user_status"),
    path('polls_list/', views.ManageActivePolls.as_view(), name="polls_list"),
    path('delete_poll/<str:poll_id>', views.DeletePoll.as_view(), name="delete_poll"),
    path('closed_poll_list/', views.ManageClosedPolls.as_view(),name="closed_poll_list"),
    path('delete_closed_poll/<str:poll_id>', views.DeleteClosedPoll.as_view(),name="delete_closed_poll"),
    

]
