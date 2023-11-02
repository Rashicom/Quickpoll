from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from . import forms
from poll.models import CustomUser, Polls, PollChoices, VotingList
import pytz
from datetime import datetime

# Create your views here.

class AdminLogin(View):

    form_class = forms.AdminUserLoginForm
    templet = "admin_login.html"

    def post(self, request):
        """
        accept: email, password
        this method validating login credencials using
        login form, then authenticate user
        """

        # creating form using data
        login_form = self.form_class(request.POST)

        # validating form
        # if the form is not valied return error response
        if not login_form.is_valid():
            print("not valied")
            return render(request, self.templet, {'error': "Pleace provide a valied email and password"})
        
        # if the form is valied procide for authentication and login
        # fetch cleaned data to authenticate
        email = login_form.cleaned_data['email']
        password = login_form.cleaned_data['password'].strip()

        # authentication
        user = authenticate(request, email=email, password=password)
        if user is not None and user.is_superuser:
            """
            AUTHENTICATED
            login() creates session and return cookies
            for authenticated user
            """
            login(request,user)
            return redirect("user_list")
        
        else:
            """
            AUTHENTICATION FAILED
            """

            # render the same page with error response
            templet = self.templet
            message = {"error":"invalied email or password"}
            
            # return
            return render(request, templet, message)


    def get(self,request):
        return render(request,"admin_login.html")



class UserManagement(View):

    templet = "users_list.html"

    def post(self,request):
        pass
    

    def get(self, request):
        user_list = CustomUser.objects.all().order_by("id")
        return render(request,self.templet,{"user_list":user_list})




# logout user
class AdminUserLogout(View):
   
    def get(self, request):
        """
        clearing sessions and redirect to login
        """

        # logout and redirect to login page
        logout(request)
        return redirect('login')





# activate or deativate user
class AlterUserStatus(View):

    def get(self, request, user_id):
        """
        accept : user_id
        this method activate or deactivate ugiven users status
        according to the present status
        retun Json response
        """
        
        try:
            # fetch user 
            user = CustomUser.objects.get(id=user_id)
            
            # if user status is True set to False if False set to True
            user.is_active = not user.is_active
            user.save()
        
        except Exception as e:
            print(e)
            return redirect("user_list")
        
        return redirect("user_list")




class ManageActivePolls(View):

    templet = "admin_active_polls.html"
    time_zone = pytz.timezone('Asia/Kolkata')

    def get(self, request):

        date_now = datetime.now(self.time_zone).date()
        polls = Polls.objects.filter(close_on__gte = date_now).order_by("poll_id")

        return render(request, self.templet, {"poll_list": polls})
    

class DeletePoll(View):

    def get(self, request, poll_id):
        """
        accept : poll_id
        this metod delete a poll
        """
        try:
            poll = Polls.objects.get(poll_id=poll_id)
            poll.delete()
        except Exception as e:
            print(e)
        
        return redirect("polls_list")