from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ArtForm(forms.Form):
    title = forms.CharField(label='title', max_length=200)
    text = forms.CharField(widget=forms.Textarea)


class AuthForm(forms.Form):
    username = forms.CharField(label='Username', max_length=200)
    password = forms.CharField(label='Password', max_length=200, widget=forms.PasswordInput())
