from django.urls import path

from .views import (AuthenticationLoginView, AuthenticationRegisterView, ConcreteGroup, CreateDeviceView, Dashboard,
                    DeviceDetail, DeviceList, GroupList, logout, update_user_groups, UserDetail, Users,
                    DeleteDeviceView,
                    UpdateDeviceView, DeviceTypeCreate, DeviceTypeList, DeviceTypeDetail, DeleteDeviceTypeView,
                    UpdateDeviceTypeView, DeviceGroupListView, CreateDeviceGroupView, DeviceGroupDetailView,
                    DeleteDeviceGroupView, UpdateDeviceGroupView)
from .views.device import share_device
from .views.device_groups import share_group

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
    path('devices/<int:pk>/delete/', DeleteDeviceView.as_view(), name='device_delete'),
    path('devices/<int:pk>/edit/', UpdateDeviceView.as_view(), name='edit_device'),
    # group
    path("groups/", GroupList.as_view(), name="groups"),
    path("group/<pk>", ConcreteGroup.as_view(), name="group"),
    path("group/<pk>/permission/add", ConcreteGroup.add_permission),
    path("group/<pk>/permission/remove", ConcreteGroup.remove_permission),
    path("users/", Users.as_view(), name="users"),
    path("user/<pk>", UserDetail.as_view(), name="user"),
    path("user/<pk>/groups", update_user_groups),
    # types
    path('device_type_create/', DeviceTypeCreate.as_view(), name='device_type_create'),
    path('device_types/', DeviceTypeList.as_view(), name='device_types'),
    path('device_type_detail/<int:pk>/', DeviceTypeDetail.as_view(), name='device_type_detail'),
    path('device_type/<int:pk>/delete/', DeleteDeviceTypeView.as_view(), name='device_type_delete'),
    path('device_type/<int:pk>/edit/', UpdateDeviceTypeView.as_view(), name='edit_device_type'),
    # device_groups
    path('device_groups/', DeviceGroupListView.as_view(), name='device_groups'),
    path('create_device_group/', CreateDeviceGroupView.as_view(), name='create_device_group'),
    path('device_groups/<int:pk>/', DeviceGroupDetailView.as_view(), name='device_group_detail'),
    path('device_groups/<int:pk>/update/', UpdateDeviceGroupView.as_view(), name='update_device_group'),
    path('device_groups/<int:pk>/delete/', DeleteDeviceGroupView.as_view(), name='delete_device_group'),
    # share device
    path('share_device/<int:pk>/', share_device, name='share_device'),
    path('share_group/<int:pk>/', share_group, name='share_group'),
]
