from django.urls import path

from .views import (AuthenticationLoginView, AuthenticationRegisterView, ConcreteGroup, CreateDeviceView, Dashboard,
                    DeviceDetail, DeviceList, GroupList, logout, update_user_groups, UserDetail, Users)

urls = [
    path("dashboard/", Dashboard.as_view(), name="dashboard"),
    # auth
    path("login/", AuthenticationLoginView.as_view(), name="login"),
    path("register/", AuthenticationRegisterView.as_view(), name="register"),
    path("logout/", logout, name="logout"),
    # device
    path("devices/", DeviceList.as_view(), name="devices"),
    path("device/<int:pk>/", DeviceDetail.as_view(), name="device_detail"),
    path("create_device/", CreateDeviceView.as_view(), name="create_device"),
    # group
    path("groups/", GroupList.as_view(), name="groups"),
    path("group/<pk>", ConcreteGroup.as_view(), name="group"),
    path("group/<pk>/permission/add", ConcreteGroup.add_permission),
    path("group/<pk>/permission/remove", ConcreteGroup.remove_permission),
    path("users/", Users.as_view(), name="users"),
    path("user/<pk>", UserDetail.as_view(), name="user"),
    path("user/<pk>/groups", update_user_groups),
]
