from django.db.models import Q

from grafita.models import Device, DeviceTypeParameter
from rest_framework import permissions, serializers, viewsets


class DeviceTypeParameterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeviceTypeParameter
        fields = ["name", "pk"]


class DeviceTypeParameterViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceTypeParameterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        device_pks = self.request.query_params.get('devices', '')

        if not device_pks:
            return DeviceTypeParameter.objects.none()

        device_type_pks = Device.objects.filter(
            Q(pk__in=device_pks.split(',')) & (Q(can_view=self.request.user) | Q(created_by=self.request.user))
        ).values_list('device_type').distinct()

        return DeviceTypeParameter.objects.filter(device_type__in=device_type_pks)
