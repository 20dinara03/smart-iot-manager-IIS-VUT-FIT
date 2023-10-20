import logging
from datetime import datetime
from typing import TypedDict

from django.db.models import QuerySet
from django.http import Http404
from django.utils import timezone
from rest_framework import serializers, views
from rest_framework.response import Response

from grafita.models import Device, Metric


class MetricSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Metric
        fields = ["time", "value", "device", "attribute"]


Dataframe: TypedDict = TypedDict("Dataframe", {"time": str, "value": float})


class MetricView(views.APIView):
    def get(self, request, device_pk, _=None):
        df = self.get_metrics_dataframe(
            self.filter_metrics(
                self.get_device(device_pk),
                self.unix_to_datetime(request.GET.get("from")),
                self.unix_to_datetime(request.GET.get("to")),
            )
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
            .order_by("attribute")
        )

    @staticmethod
    def get_metrics_dataframe(metrics: QuerySet[Metric]) -> dict[str, dict[str, list[Dataframe]]]:
        df: dict[str, dict[str, list[Dataframe]]] = {}  # type: ignore
        for metric in metrics.iterator():
            attr = df.get(metric["attribute"])
            if attr:
                attr["time"].append(metric["time"])
                attr["value"].append(metric["value"])
            else:
                df[metric["attribute"]] = {"time": [metric["time"]], "value": [metric["value"]]}

        return df

    @staticmethod
    def get_device(device_pk: int) -> Device:
        try:
            return Device.objects.filter(id=device_pk).get()
        except Device.DoesNotExist:
            raise Http404
