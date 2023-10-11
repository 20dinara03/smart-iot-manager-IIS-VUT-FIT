from django.urls import path

from .views import (
    AuthenticationLoginView,
    AuthenticationRegisterView,
    Dashboard,
    logout,
    GroupList,
    ConcreteGroup,
    Users,
    UserDetail,
    update_user_groups,
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
    path("users/", Users.as_view(), name="users"),
    path("user/<pk>", UserDetail.as_view(), name="user"),
    path("user/<pk>/groups", update_user_groups),
]
