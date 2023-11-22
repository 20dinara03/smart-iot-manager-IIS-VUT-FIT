from django.urls import include, path
from rest_framework import routers

from .device import DeviceGroupViewSet, DeviceTypeViewSet, DeviceViewSet, KPIViewSet
from .device_type import DeviceTypeParameterViewSet
from .group import GroupViewSet
from .metric import MetricView
from .user import UserViewSet

__all__ = ["rest_urls"]

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'device_groups', DeviceGroupViewSet, basename='device_group')
router.register(r'device_types', DeviceTypeViewSet, basename='device_type')
router.register(r'device_parameters', DeviceTypeParameterViewSet, basename='device_parameters')
router.register(r'kpis', KPIViewSet, basename='kpi')

rest_urls = [
    path('device/<int:device_pk>/metrics', MetricView.as_view(), name='metrics'),
    path('', include(router.urls), name='rest'),
]
