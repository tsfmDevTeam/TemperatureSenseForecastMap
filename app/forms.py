# from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser


class SignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]


class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "password"]
