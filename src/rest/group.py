from django.contrib.auth.models import Group, Permission
from rest_framework import serializers

from rest import ViewForAdmins


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)


    class Meta:
        model = Group
        fields = ["name", "permissions"]


class GroupViewSet(ViewForAdmins):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
