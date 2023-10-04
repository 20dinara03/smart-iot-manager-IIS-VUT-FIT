from typing import Final, TypedDict

from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import FormView
from django.views.generic.base import ContextMixin

LoginFormDict = TypedDict("LoginFormDict", {
    "username": str,
    "password": str,
})


class LoginForm(forms.Form):
    username: Final = forms.CharField()
    password: Final = forms.CharField(widget=forms.PasswordInput)

    def is_valid(self):
        form = self.get_context()["form"].clean()
        # TODO:
        return form["username"] != "admin"


class RegisterForm(LoginForm):
    email: Final = forms.EmailField()
    password2: Final = forms.CharField(widget=forms.PasswordInput)


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
        context = self.get_context_data(form=form)
        context.update({"error": "Invalid username or password."})
        return render(self.request, self.template_name, context)


class AuthenticationRegisterView(AuthenticationLoginView):
    form_class = RegisterForm
