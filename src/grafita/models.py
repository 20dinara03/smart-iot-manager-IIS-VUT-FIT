from django.contrib.auth.models import User
from django.db import models
from timescale.db.models.models import TimescaleDateTimeField, TimescaleModel


class DeviceGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()


class DeviceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()


class Device(models.Model):
    name = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)
    device_group = models.ForeignKey(DeviceGroup, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    value_min = models.FloatField(null=True, blank=True)
    value_max = models.FloatField(null=True, blank=True)
    default_kpi = models.ForeignKey("KPI", on_delete=models.SET_NULL, null=True, blank=True)


class KPI(models.Model):
    name = models.CharField(max_length=100)


class Metric(TimescaleModel):
    time = TimescaleDateTimeField(interval="10 min")

    value = models.FloatField()
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
