from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms


class LoginForm(ModelForm):
    class Meta:
        model = User
        widgets = {'password': forms.PasswordInput}
        fields = ['username', 'password']
