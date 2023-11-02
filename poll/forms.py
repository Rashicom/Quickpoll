from django import forms
from .models import CustomUser, Polls, PollChoices, VotingList


class UserLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.Field(required=True)


class SignupForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'password']


class PollsForm(forms.Form):
    poll_question = forms.CharField()
    close_on = forms.DateField()    

    

class VotingForm(forms.Form):
    poll_id = forms.IntegerField()
    pollchoice_id = forms.IntegerField()
    