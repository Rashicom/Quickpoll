from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.UserLogin.as_view(), name="login"),
    path('active_polling/', views.Home.as_view(), name="active_polling"),
    path('signup/', views.SignUp.as_view(), name="signup"),
    path('closed_polling/', views.Results.as_view(), name="closed_polling"),
    path('logout/', views.UserLogout.as_view(),name="logout"),
    
]