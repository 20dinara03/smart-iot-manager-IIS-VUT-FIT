from django.contrib.auth.models import Group, User
from rest_framework import serializers
from rest import ViewForAdmins


class UserSerializer(serializers.HyperlinkedModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True)

    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class UserViewSet(ViewForAdmins):
    queryset = User.objects.all()
    serializer_class = UserSerializer
