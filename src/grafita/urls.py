from django.urls import path


from .views import Dashboard, AuthenticationLoginView, AuthenticationRegisterView, logout

urls = [
    path("dashboard/", Dashboard.as_view(), name="dashboard"),
    path("login/", AuthenticationLoginView.as_view(), name="login"),
    path("register/", AuthenticationRegisterView.as_view(), name="register"),
    path("logout/", logout, name="logout"),
]
