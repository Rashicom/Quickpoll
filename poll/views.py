from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from . import forms
from . models import CustomUser, Polls, PollChoices, VotingList
from django.db import transaction
from datetime import datetime
import pytz

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
    time_zone = pytz.timezone('Asia/Kolkata')

    @method_decorator(login_required(login_url="login"))
    def get(self, request):
        """
        home page contains active pollings which can see both 
        authenticated and non authenticated users
       
        anouthenticated action trigger the redirection to login page
        """


        date_now = datetime.now(self.time_zone).date()
        # polls = Polls.objects.filter(close_on__gte = date_now).prefetch_related('poll_choice_set')
        polls = Polls.objects.all().prefetch_related('poll_choice_set')
        
        poll_list = []
        for poll in polls:
            new_poll = {
                "user":poll.user,
                "poll_id": poll.poll_id,
                "poll_question": poll.poll_question,
                "published_on":poll.published_on,
                "close_on":poll.close_on,
                "total_vote_count":poll.total_vote_count,
                "choice":[]
            }

            for choice in poll.poll_choice_set.all():

                # calculate percent
                try:
                    percent = (100/poll.total_vote_count) * choice.vote_count
                except Exception as e:
                    percent = 0

                new_poll["choice"].append({
                    "pollchoice_id":choice.pollchoice_id,
                    "choice_discription":choice.choice_discription,
                    "vote_count":choice.vote_count,
                    "percent":percent
                })

            poll_list.append(new_poll)
        
        return render(request, self.templet,{"poll_list":poll_list})    


        


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



class Vote(View):

    form_class = forms.VotingForm


    @method_decorator(login_required(login_url="login"))
    @transaction.atomic
    def post(self, request):
        """
        accept : poll_id, pollchoice_id
        record a voating and return json response
        """

        # validate form
        voting_form = self.form_class(request.POST)
        if not voting_form.is_valid():
            return JsonResponse({"status":400, "message":"Invalied data"})
        

        try:
            user = request.user
            poll_id = voting_form.cleaned_data.get('poll_id')
            pollchoice_id = voting_form.cleaned_data.get('pollchoice_id')

            # increase count of votes
            poll_instance = Polls.objects.get(poll_id=poll_id)
            poll_instance.total_vote_count += 1
            
            pollchoice_instance = PollChoices.objects.get(pollchoice_id=pollchoice_id)
            pollchoice_instance.vote_count += 1
            
            VotingList.objects.create(
                user = user,
                poll_id = poll_instance,
                pollchoice_id = pollchoice_instance
            )

            poll_instance.save()
            pollchoice_instance.save()

        except Exception as e:
            print(e)
            return JsonResponse({"status":200, "message":"Response already recorded"})

        return JsonResponse({"status":201, "message":"Response successfully recorded"})



class ClosedPolls(View):

    templet = "closed_polling.html"
    time_zone = pytz.timezone('Asia/Kolkata')

    @method_decorator(login_required(login_url="login"))
    def get(self, request):
        """       
        returns closed polling details
        """

        # fetching todays date to compare with the poll date
        date_now = datetime.now(self.time_zone).date()
        polls = Polls.objects.filter(close_on__lt = date_now).prefetch_related('poll_choice_set')
        
        # creating a list of datas fron poll, choice and voting lists to show in the html
        poll_list = []
        for poll in polls:
            
            # creating a dict for for each polls with required values
            new_poll = {
                "user":poll.user,
                "poll_id": poll.poll_id,
                "poll_question": poll.poll_question,
                "published_on":poll.published_on,
                "close_on":poll.close_on,
                "total_vote_count":poll.total_vote_count,
                "choice":[]
            }

            for choice in poll.poll_choice_set.all():

                # calculate percent
                try:
                    percent = (100/poll.total_vote_count) * choice.vote_count
                except Exception as e:
                    percent = 0

                # appending choice details
                new_poll["choice"].append({
                    "pollchoice_id":choice.pollchoice_id,
                    "choice_discription":choice.choice_discription,
                    "vote_count":choice.vote_count,
                    "percent":percent
                })

            # after all data is collected and created a new_poll, append it to the poll_list
            poll_list.append(new_poll)
       
        return render(request, self.templet,{"poll_list":poll_list})



class MyPolls(View):

    templet = "my_polling.html"
    time_zone = pytz.timezone('Asia/Kolkata')

    @method_decorator(login_required(login_url="login"))
    def get(self, request):
        """       
        returns closed polling details
        """

        # fetching todays date to compare with the poll date
        date_now = datetime.now(self.time_zone).date()
        polls = Polls.objects.filter(user=request.user).prefetch_related('poll_choice_set')
        
        # creating a list of datas fron poll, choice and voting lists to show in the html
        active_list = []
        closed_list = []
        for poll in polls:
            
            # creating a dict for for each polls with required values
            new_poll = {
                "user":poll.user,
                "poll_id": poll.poll_id,
                "poll_question": poll.poll_question,
                "published_on":poll.published_on,
                "close_on":poll.close_on,
                "total_vote_count":poll.total_vote_count,
                "choice":[]
            }

            for choice in poll.poll_choice_set.all():

                # calculate percent
                try:
                    percent = (100/poll.total_vote_count) * choice.vote_count
                except Exception as e:
                    percent = 0

                # appending choice details
                new_poll["choice"].append({
                    "pollchoice_id":choice.pollchoice_id,
                    "choice_discription":choice.choice_discription,
                    "vote_count":choice.vote_count,
                    "percent":percent
                })

            # after all data is collected and created a new_poll, append it to the poll_list
            # check the date with todays date
            # if the closed date is passed , then add new_poll to the my_poll_list
            # if the still poll is actived, then add new_poll to the poll_list
            if poll.close_on >= date_now:
                active_list.append(new_poll)
                
            elif poll.close_on < date_now:
                closed_list.append(new_poll)
            else:
                print("cant check the date")
        
       
        return render(request, self.templet,{"closed_list":closed_list,"active_list":active_list})