from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.UserLogin.as_view(), name="login"),
    path('active_polling/', views.Home.as_view(), name="active_polling"),
    path('signup/', views.SignUp.as_view(), name="signup"),
    path('closed_polling/', views.ClosedPolls.as_view(), name="closed_polling"),
    path('logout/', views.UserLogout.as_view(),name="logout"),
    path('add_poll/', views.AddPoll.as_view(), name="add_poll"),
    path('vote/', views.Vote.as_view(), name="vote"),
    path('my_poll/', views.MyPolls.as_view(), name="my_poll"),

]

