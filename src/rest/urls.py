from rest_framework import routers

from .group import GroupViewSet
from .user import UserViewSet
from .device import DeviceViewSet, DeviceGroupViewSet, DeviceTypeViewSet, MetricViewSet, KPIViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'device_groups', DeviceGroupViewSet, basename='device_group')
router.register(r'device_types', DeviceTypeViewSet, basename='device_type')
router.register(r'metrics', MetricViewSet, basename='metric')
router.register(r'kpis', KPIViewSet, basename='kpi')
