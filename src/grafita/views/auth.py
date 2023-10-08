from typing import Final, TypedDict

from django import forms
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import FormView
from django.views.generic.base import ContextMixin

LoginFormDict = TypedDict("LoginFormDict", {
    "username": str,
    "password": str,
})


class LoginForm(forms.ModelForm):
    template_name = "snippets/standard_form.html"
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username", "class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["username", "password"]

    def validate_unique(self):
        pass


class RegisterForm(LoginForm):
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"}))

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]


    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            return False
        data = self.clean()
        if data["password"] != data["password2"]:
            self.add_error("password2", "Passwords do not match.")
            return False
        return True


class AuthenticationLoginView(FormView):
    template_name: Final = "login.html"
    form_class_dict: Final = {"login": LoginForm, "register": RegisterForm}
    form_class = LoginForm
    success_url: Final = "/dashboard"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)
        kwargs.update(self.form_class_dict)
        return render(request, self.template_name, kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update(self.form_class_dict)
        return ContextMixin.get_context_data(self, **kwargs)

    def form_invalid(self, form):
        context = self.get_context_data()
        for value in form.errors.values():
            context["error"] = value
            break
        return render(self.request, self.template_name, context)

    def form_valid(self, form):
        form = form.clean()
        user = authenticate(username=form["username"], password=form["password"])

        if user is not None:
            login(self.request, user)
            return HttpResponseRedirect(self.success_url)
        context = self.get_context_data()
        context["error"] = "Invalid username or password."
        return render(self.request, self.template_name, context)


def logout(request):
    django_logout(request)
    return HttpResponseRedirect("/")


class AuthenticationRegisterView(AuthenticationLoginView):
    form_class = RegisterForm

    @staticmethod
    def get_error_if_exists(form) -> str:
        """ Check if the form is valid.
        """
        data = form.clean()

        if User.objects.filter(username=data["username"]).exists():
            return "Username already exists."

    def form_valid(self, form) -> HttpResponseRedirect:
        error = self.get_error_if_exists(form)

        if error:
            context = self.get_context_data()
            context["error"] = error
            return render(self.request, self.template_name, context)

        self.create_and_login(form)

        return HttpResponseRedirect(self.success_url)

    def create_and_login(self, form) -> None:
        data = form.clean()
        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
        )
        login(self.request, user)
