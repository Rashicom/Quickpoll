from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name="active_polling"),
    path('login/', views.UserLogin.as_view(), name="login"),
    path('signup/', views.SignUp.as_view(), name="signup"),
    path('result/', views.Results.as_view(), name="result"),
    path('logout/', views.UserLogout.as_view(),name="logout"),
    
]