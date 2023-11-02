from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from . import forms
from . models import CustomUser, Polls, PollChoices, VotingList
from django.db import transaction

# Create your views here.

class UserLogin(View):

    templet = "login.html"
    form_class = forms.UserLoginForm

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
        if user is not None:
            """
            AUTHENTICATED
            login() creates session and return cookies
            for authenticated user
            """
            login(request,user)
            return redirect("active_polling")
        
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

        # if user is already authenticated redirect to the polling page
        if request.user.is_authenticated:
            return redirect("active_polling")
        
        return render(request,self.templet)




class SignUp(View):

    templet = "signup.html"
    form_class = forms.SignupForm

    def post(self,request):

        # creating form
        signup_form = self.form_class(request.POST)

        # validating form
        # if the form is not valied return error response
        if not signup_form.is_valid():
            print("not valied")
            print(signup_form.errors)
            return render(request, self.templet, {'error': "Pleace provide credencials"})
        
        try:
            email = signup_form.cleaned_data['email']
            first_name = signup_form.cleaned_data['first_name']
            password = signup_form.cleaned_data['password']
            user = CustomUser.objects.create_user(email=email,first_name=first_name,password=password)
        
        except Exception as e:
            print(e)
            return render(request, self.templet, {'error': "User already exist"})

        # if user is created, login and redirect to the active pollign window
        login(request,user)
        return redirect("active_polling")


    def get(self,request):
        return render(request,self.templet)



# logout user
class UserLogout(View):

    
    def get(self, request):
        """
        clearing sessions and redirect to login
        """

        # logout and redirect to login page
        logout(request)
        return redirect('login')



class Home(View):

    templet = "active_polling.html"

    @method_decorator(login_required(login_url="login"))
    def get(self, request):
        """
        home page contains active pollings which can see both 
        authenticated and non authenticated users
       
        anouthenticated action trigger the redirection to login page
        """
        return render(request, self.templet)    



class Results(View):

    templet = "closed_polling.html"

    @method_decorator(login_required(login_url="login"))
    def get(self, request):

        return render(request,self.templet)
        


# ajax call to add new poll
class AddPoll(View):

    form_class = forms.PollsForm

    @method_decorator(login_required(login_url="login"))
    @transaction.atomic
    def post(self, request):
        """
        accept : question, end_on, choices(array)
        after creating a new poll 
        return json response
        """

        # fetching data
        choice_list = request.POST.getlist('choice_list[]')
        user = request.user
        poll_form = self.form_class(request.POST)
        
        # validating form, additionally check the choice_list is empty or not
        if not poll_form.is_valid() or len(choice_list) <= 1:
            print(poll_form.errors)
            return JsonResponse({"status":400,"message":"inbvalied data"})

        # create record and return response
        try:
            poll_question = poll_form.cleaned_data.get("poll_question")
            close_on = poll_form.cleaned_data.get("close_on")
            new_poll = Polls.objects.create(
                user = user,
                poll_question = poll_question,
                close_on = close_on
            )
            
            # update all choices in in the choice list
            for choice in choice_list:
                PollChoices.objects.create(poll_id=new_poll,choice_discription=choice)

        except Exception as e:
            print(e)
            return JsonResponse({"status":400, "message":"invalied data"})
        return JsonResponse({"status":201, "message":"created"})
