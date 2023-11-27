import logging
from datetime import datetime
from functools import partial
from typing import TypedDict

from django.db.models import QuerySet
from django.http import Http404
from django.utils import timezone
from rest_framework import serializers, views
from rest_framework.response import Response

from grafita.kpi import kpi_registry
from grafita.models import Device, DevicesGroup, Metric


class MetricSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Metric
        fields = ["time", "value", "device", "attribute"]


Dataframe: TypedDict = TypedDict("Dataframe", {"time": str, "value": float})


class MetricView(views.APIView):
    def get(self, request, device_pk, _=None):
        group_pk = request.GET.get("group")
        if not group_pk:
            raise Http404

        df = self.get_metrics_dataframe(
            self.filter_metrics(
                self.get_device(device_pk),
                self.unix_to_datetime(request.GET.get("from")),
                self.unix_to_datetime(request.GET.get("to")),
            ),
            DevicesGroup.objects.get(id=group_pk),
        )
        return Response(df)

    @staticmethod
    def unix_to_datetime(unix):
        if unix:
            return datetime.fromtimestamp(int(unix), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S %z")

    @staticmethod
    def filter_metrics(device: Device, f, t) -> QuerySet[Metric]:
        kw = {}
        if f and t:
            kw["time__range"] = (f, t)
        elif f:
            kw["time__gte"] = f
        elif t:
            kw["time__lte"] = t

        return (
            Metric.objects.filter(
                device=device,
                **kw,
            )
            .values("time", "value", "attribute")
            .order_by("time")[:30]
        )

    @staticmethod
    def get_metrics_dataframe(metrics: QuerySet[Metric], group: DevicesGroup) -> dict[str, dict[str, list[Dataframe]]]:
        df: dict[str, dict[str, list[Dataframe]]] = {}  # type: ignore

        validators = {}
        for metric in metrics.iterator():
            attribute_name = metric["attribute"]
            if attribute_name not in validators:
                kpi = group.kpi_set.filter(parameter__name=attribute_name).first()
                if not kpi:
                    logging.warning(f"KPI for {attribute_name} not found")
                    return df
                validators[attribute_name] = partial(kpi_registry[kpi.class_name].val, threshold=kpi.value)

            attr = df.get(attribute_name)
            if attr:
                attr["color"].append(validators[attribute_name](metric["value"]))
                attr["time"].append(metric["time"])
                attr["value"].append(metric["value"])
            else:
                df[attribute_name] = {
                    "color": [validators[attribute_name](metric["value"])],
                    "time": [metric["time"]],
                    "value": [metric["value"]]
                }

        return df

    @staticmethod
    def get_device(device_pk: int) -> Device:
        try:
            return Device.objects.filter(id=device_pk).get()
        except Device.DoesNotExist:
            raise Http404
