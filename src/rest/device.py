from django.contrib.auth.models import User
from rest_framework import serializers
from grafita.models import Device, DevicesGroup, DeviceType, KPI, DeviceTypeParameter
from rest import ViewForAdmins


class DeviceGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DevicesGroup
        fields = ["name"]


class DeviceGroupViewSet(ViewForAdmins):
    queryset = DevicesGroup.objects.all()
    serializer_class = DeviceGroupSerializer


class DeviceTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeviceType
        fields = ["name", "description"]


class DeviceTypeViewSet(ViewForAdmins):
    queryset = DeviceType.objects.all()
    serializer_class = DeviceTypeSerializer


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    device_type = serializers.PrimaryKeyRelatedField(queryset=DeviceType.objects.all())
    default_kpi = serializers.PrimaryKeyRelatedField(queryset=KPI.objects.all())
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Device
        fields = ["name", "model", "location", "device_type", "default_kpi", "created_by"]


class DeviceViewSet(ViewForAdmins):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class KPISerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = KPI
        fields = ["name", "value"]


class KPIViewSet(ViewForAdmins):
    queryset = KPI.objects.all()
    serializer_class = KPISerializer


class DeviceTypeParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceTypeParameter
        fields = ['name', 'min_value', 'max_value']
