from django.urls import path

from .views import (
    AuthenticationLoginView,
    AuthenticationRegisterView,
    Dashboard,
    logout,
    GroupList,
    ConcreteGroup,
)

urls = [
    path("dashboard/", Dashboard.as_view(), name="dashboard"),
    # auth
    path("login/", AuthenticationLoginView.as_view(), name="login"),
    path("register/", AuthenticationRegisterView.as_view(), name="register"),
    path("logout/", logout, name="logout"),
    # group
    path("groups/", GroupList.as_view(), name="groups"),
    path("group/<pk>", ConcreteGroup.as_view(), name="group"),
    path("group/<pk>/permission/add", ConcreteGroup.add_permission),
    path("group/<pk>/permission/remove", ConcreteGroup.remove_permission),
]
