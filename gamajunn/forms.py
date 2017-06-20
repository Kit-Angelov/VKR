from django import forms
from django.forms import TextInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from ckeditor.widgets import CKEditorWidget


class ArtForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Заголовок статьи'}))
    text = forms.CharField(widget=CKEditorWidget(config_name='default'))


class AuthForm(forms.Form):
    username = forms.CharField(label='Username', max_length=200)
    password = forms.CharField(label='Password', max_length=200, widget=forms.PasswordInput())


class RegistrationForm(UserCreationForm):
    #email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}),required = True)
    #first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}),required = False)
    #last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),required = False)
    username = forms.CharField(widget=forms.TextInput(attrs={'value': 'Логин'}), required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'value': 'Пароль'}), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'value': 'Повторите пароль'}), required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Set field Label as Placeholder for every field
        self.fields['username'].widget.attrs['placeholder'] = 'Login'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        #user.email = self.cleaned_data['email']
        #user.first_name = self.cleaned_data['first_name']
        #user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
        return user
