from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, CreateView

from django.conf import settings
from .forms import LoginUserForm, ProfileUserForm, RegisterUserForm, UserPasswordChangeForm



class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}

    # def get_success_url(self):
    #     return reverse_lazy('core:home')


# /Авторизация пользователей с помощью стандартного класса

# Профиль пользователя
class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': "Профиль пользователя", 'default_image': settings.DEFAULT_USER_IMAGE}

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


# /Профиль пользователя/

# Регистрация пользователя с помощью функции
# def register_user(request):
#     if request.method == 'POST':
#         form = RegisterUserForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])
#             user.save()
#             return render(request, 'users/register_done.html')
#     else:
#         form = RegisterUserForm()
#     return render(request, 'users/register.html', {'form': form})
# /Регистрация пользователя с помощью функции

# Регистрация пользователя с помощью класса  CreateView
class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('users:register_done')


def register_done(request):
    '''
        Страница сообщающая что пользователь успешно зарегистрирован
    '''
    return render(request, 'users/register_done.html')


class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password_change_form.html"
    extra_context = {'title': "Изменение пароля"}