from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from timescale.db.models.models import TimescaleDateTimeField, TimescaleModel


class DevicesGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_groups')
    devices = models.ManyToManyField('Device', related_name='device_groups')
    shared_with = models.ManyToManyField(User, related_name='shared_groups')
    requested_by = models.ManyToManyField(User, related_name='request_users')

    def __str__(self):
        return self.name


class DeviceType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_types')

    def __str__(self):
        return self.name


class DeviceTypeParameter(models.Model):
    name = models.CharField(max_length=100, null=True)
    min_value = models.IntegerField(default=0)
    max_value = models.IntegerField(default=100)
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)


class Device(models.Model):
    name = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, null=True, blank=True)
    device_group = models.ForeignKey(DevicesGroup, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='devices_of_group')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    can_view = models.ManyToManyField(User, related_name='can_view_devices')

    def __str__(self):
        return self.name

    def validate_kpi(self, time_from, time_to) -> bool:
        """ Should:

        Interfaces:
            In:
                (device ID)
            Out:
                Dataframe

        - Get an object from database -> refs to lazy KPI.
            - in: (device ID)
            - out: KPI (value, formula)
            - calculate via available data
            - create dataframe with annotation if a device is valid by KPI

        """
        pass


class KPI(models.Model):
    class_name = models.CharField(max_length=100)
    parameter = models.ForeignKey(DeviceTypeParameter, on_delete=models.CASCADE, null=True)
    value = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    device_group = models.ForeignKey(DevicesGroup, on_delete=models.CASCADE, null=True, blank=True)


class Metric(TimescaleModel):
    time = TimescaleDateTimeField(interval="10 min")

    value = models.FloatField()
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    attribute = models.CharField(max_length=100)
