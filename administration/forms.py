from django import forms

class AdminUserLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.Field(required=True)