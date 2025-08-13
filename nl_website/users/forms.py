import datetime
from django.core.validators import *
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm

from django_password_eye.fields import PasswordEye
from django_password_eye.widgets import PasswordEyeWidget


class LoginUserForm(AuthenticationForm):
    # username = forms.CharField(label="Логин", widget=forms.TextInput())
    # password = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    username = forms.CharField(max_length=150,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ('Login')}),
                               label='')
    password = PasswordEye(label='')

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(disabled=True, label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(disabled=True, label='E-mail', widget=forms.TextInput(attrs={'class': 'form-control'}))
    # date_joined = forms.DateTimeField(disabled=True, label='Дата регистрации ')

    class Meta:
        model = get_user_model()
        fields = ['avatar', 'username', 'email', 'first_name', 'last_name']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = PasswordEye(label='')
    password2 = PasswordEye(label='')

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'email': 'Email (потребуется для восстановления пароля)',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': PasswordEyeWidget(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким e-mail уже существует')
        return email

class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
