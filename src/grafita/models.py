from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import QuerySet
from timescale.db.models.models import TimescaleDateTimeField, TimescaleModel

from grafita.kpi import AnyKpi, kpi_registry


class DeviceGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)


class DeviceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    attributes = ArrayField(models.CharField(max_length=100), null=True, blank=True)

    def __str__(self):
        return self.name


class DeviceTypeParameter(models.Model):
    name = models.CharField(max_length=100)
    min_value = models.IntegerField()
    max_value = models.IntegerField()
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)


class Device(models.Model):
    name = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, null=True, blank=True)
    device_group = models.ForeignKey(DeviceGroup, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    value_min = models.FloatField(null=True, blank=True)
    value_max = models.FloatField(null=True, blank=True)
    default_kpi = models.ForeignKey("KPI", on_delete=models.SET_NULL, null=True, blank=True)

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
        metrics: QuerySet[Metric] = Metric.objects.filter(device=self.id).filter(time__range=(time_from, time_to))
        kpi: AnyKpi = kpi_registry[self.default_kpi.name]
        return kpi.validate(self.default_kpi.value, metrics)


class KPI(models.Model):
    name = models.CharField(max_length=100)
    value = ArrayField(models.DecimalField(max_digits=6, decimal_places=2), size=5, null=True, blank=True)


class Metric(TimescaleModel):
    time = TimescaleDateTimeField(interval="10 min")

    value = models.FloatField()
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    attribute = models.CharField(max_length=100)
